from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
from enum import Enum, auto
from shutil import rmtree
from subprocess import Popen, PIPE, CalledProcessError
import contextlib
import glob
import os
import re
import subprocess
import sys
import tempfile

class Os(Enum):
    LINUX = auto()
    OSX = auto()
    WIN = auto()


def get_os():
    platform = sys.platform.lower()

    if platform.startswith("linux"):
        return Os.LINUX
    elif platform.startswith("darwin"):
        return Os.OSX
    elif platform.startswith("win"):
        return Os.WIN
    else:
        raise Exception(f"Unsupported platform: {platform}")


OS = get_os()
PYTHON = sys.executable
VALID_PYTHON_VERSION_PATTERN = "python 3\.[67][^\d]"

# this depends on pwd being in the scripts directory
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
BACKEND_SRC = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_SRC_ROOT = os.path.join(PROJECT_ROOT, "frontend")
RYGG_DIR = os.path.join(PROJECT_ROOT, "rygg")
FILESERVER_DIR = os.path.join(PROJECT_ROOT, "fileserver")
WHEELFILES_DIR = os.path.join(PROJECT_ROOT, "wheelfiles")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
BUILD_TMP = os.path.join(BUILD_DIR, "tmp")
BUILD_OUT = os.path.join(BUILD_DIR, "out")

BUILD_DOCKER = os.path.join(BUILD_DIR, "docker")
BUILD_DOCKER_FRONTEND = os.path.join(BUILD_DOCKER, "frontend")
BUILD_DOCKER_RYGG = os.path.join(BUILD_DOCKER, "rygg")
BUILD_DOCKER_KERNEL = os.path.join(BUILD_DOCKER, "kernel")

build_reason = os.environ.get("BUILD_REASON")
build_num = os.environ.get("BUILD_NUM")

# The python stuff uses PEP440 as the version string, while
# the npm-based stuff uses semver. They're not compatible when
# we're tacking on the build number for nightly builds
class Versions():

    def __init__(self, version_str, extension=None):
        from semver import VersionInfo as SemVersion
        from packaging.version import Version as PepVersion

        if extension:
            self._as_semver = SemVersion.parse(f"{version_str}-{extension}")
            self._as_pep440 = PepVersion(f"{version_str}.{extension}")
        else:
            self._as_semver = SemVersion.parse(version_str)
            self._as_pep440 = PepVersion(version_str)

    def __repr__(self):
        s = self.as_semver
        p = self.as_pep440
        return f"<Versions(as_semver={s}, as_pep440={p})>"

    @property
    def as_semver(self):
        return str(self._as_semver)

    @property
    def as_pep440(self):
        return str(self._as_pep440)

@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


def all_lines(filename):
    with open(filename, "r") as f:
        return f.readlines()


def sub_all(arr, pattern, replacement):
    return [re.sub(pattern, replacement, l) for l in arr]


def write_all_lines(filename, lines):
    with open(filename, "w") as f:
        f.writelines(lines)


def sed_i(filename, pattern, replacement):
    transformed = [re.sub(pattern, replacement, l) for l in all_lines(filename)]
    write_all_lines(filename, transformed)


def rm_rf(dirname):
    if os.path.exists(dirname):
        rmtree(dirname)


def copy_files(src_root, dest_root, list_path=None):
    if list_path:
        with open(list_path) as f:
            lines = [
                l.strip()
                for l in f.readlines()
                if not bool(re.match("^ *$", l)) and not bool(re.match("^ *#", l))
            ]

            for l in lines:
                src = os.path.join(src_root, l)
                dest = os.path.join(dest_root, l)
                print(f"{src} -> {dest}")

                if os.path.isfile(src):
                    dirname = os.path.dirname(dest)
                    mkdir_p(dirname)
                    copy_file(src, dest, update=True)
                elif os.path.isdir(src):
                    dirname = os.path.dirname(dest)
                    copy_tree(src, dest, update=True)
                else:
                    print(f"Skipping non-file: {src}")
                    continue
    elif os.path.isfile(src_root):
        copy_file(src_root, dest_root, update=True)
    elif os.path.isdir(src_root):
        copytree(src_root, dest_root)

def run_checked_arr(arr, env=None):
    inner={} if not env else {"env":{**env, **os.environ}}
    with Popen(arr, stdout=PIPE, bufsize=1, universal_newlines=True, **inner) as p:
        for line in p.stdout:
            print(line, end="")  # process line here

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)


def run_checked(cmd, env=None):
    print(f"$ {cmd}")
    as_arr = cmd.split()
    run_checked_arr(as_arr, env=env)


def run_unchecked(cmd):
    print(f"$ {cmd}")
    as_arr = cmd.split()
    with Popen(as_arr, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end="")  # process line here


def run(cmd):
    as_arr = cmd.split()
    subprocess.call(as_arr)


def get_run_checked(cmd):
    print(f"$ {cmd}")
    as_arr = cmd.split()
    return str(subprocess.check_output(as_arr))


def mkdir_p(dirname):
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def generate_included_files_common():
    projects = "perceptilabs_runner rygg fileserver backend".split()
    for p in projects:
        for line in all_lines(f"{PROJECT_ROOT}/{p}/included_files.txt"):
            stripped = line.strip()
            if len(stripped) == 0:
                continue
            if stripped.startswith("#"):
                continue

            yield f"{p}/{stripped}"

@contextlib.contextmanager
def included_files_common():
    lines = [l+'\n' for l in generate_included_files_common()]
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.writelines(lines)
        tmp.flush()
        tmp.close()
        yield tmp.name

def assert_python_version():

    ver = get_run_checked("python --version")
    if not bool(re.search(VALID_PYTHON_VERSION_PATTERN, ver, re.IGNORECASE)):
        raise Exception(f"Unsupported python version: {ver}")

    ver = get_run_checked("pip --version")
    if not bool(re.search(VALID_PYTHON_VERSION_PATTERN, ver, re.IGNORECASE)):
        raise Exception(
            f"Wrong python version ({ver}). Have you set up your virtualenv?"
        )


def train_models():
    with pushd(f"{BACKEND_SRC}/perceptilabs/insights/csv_ram_estimator"):
        run_checked("python train_model.py data_1579288530.csv")


def install_prereqs():
    if OS == Os.LINUX:
        run_checked("bash set_up_linux.bash")
    elif OS == Os.OSX:
        run_checked("bash set_up_osx.bash")
    elif OS == Os.WIN:
        run_checked("cmd /c set_up_windows.bat")
    else:
        raise Exception(f"Integration error: OS={OS}")

    run_checked("python -m pip install --upgrade pip setuptools wheel")

    if OS == Os.WIN:
        run_unchecked('pip install gym[atari]')
        run_unchecked("pip install -U git+https://github.com/Kojoley/atari-py.git")

    run_checked(f"pip install -r {BACKEND_SRC}/requirements.txt")
    run_checked(f"pip install -r {RYGG_DIR}/requirements.txt")
    run_checked(f"pip install -r {FILESERVER_DIR}/requirements.txt")
    run_unchecked("pip install -r requirements_build.txt")

def install_docker_host_prereqs():
    run_unchecked("pip install semver>=2.10")
    run_unchecked("pip install packaging>=20.4")


# Pull from the VERSION file with optional overrides in VERSION_OVERRIDE and VERSION_EXTENSION
def calc_version():
    # it sometimes happens that Win scripts append an extra quote. Strip it.
    def get_clean_env_var(name):
        ret = os.environ.get(name)
        return ret.replace('"', '') if ret else None

    override = get_clean_env_var("VERSION_OVERRIDE")
    if override:
        return Versions(override)

    with open(os.path.join(PROJECT_ROOT, "VERSION"), "r") as f:
        version_str = f.read().strip().replace('"', '')

    extension = get_clean_env_var("VERSION_EXTENSION")
    return Versions(version_str, extension=extension)


def set_perceptilabs_inner_version(rootDir, versions: Versions):
    init_py = os.path.join(rootDir, "perceptilabs", "__init__.py")
    sed_i(init_py, "^__version__ *=.*", f"__version__='{versions.as_pep440}'")


def set_rygg_inner_version(rootDir, versions: Versions):
    init_py = os.path.join(rootDir, "rygg", "__init__.py")
    sed_i(init_py, "^__version__ *=.*", f"__version__='{versions.as_pep440}'")

def write_version_file(rootDir, versions: Versions):
    with open(f"{rootDir}/VERSION", "w") as f:
        f.write(versions.as_pep440)

def set_wheel_version(versions: Versions):
    print(f"setting wheel version to {versions.as_pep440}")
    write_version_file(BUILD_TMP, versions)
    set_perceptilabs_inner_version(BUILD_TMP, versions)
    set_rygg_inner_version(BUILD_TMP, versions)

# update the version field in the package.json file
def set_frontend_version(package_json_file, versions: Versions):
    import json

    with open(package_json_file, "r") as f:
        as_dict = json.load(f)

    as_dict["version"] = versions.as_semver

    with open(package_json_file, "w") as f:
        json.dump(as_dict, f, indent=2)


def get_wheel_name():
    ret = os.environ.get("PACKAGE_NAME_OVERRIDE") or "perceptilabs"
    # windows tools don't auto-substitute
    return ret.replace("-", "_").replace('"', '')


def set_wheel_name(package_name):
    print(f"Setting wheel name to {package_name}")
    # unlike the version metadata, setuptools doesn't support loading from an external file
    # ... so we hack the config directly
    sed_i(f"{BUILD_TMP}/setup.cfg", "^name *=.*$", f"name={package_name}")


# PATH isn't obeyed correctly on windows
def npm_cmd():
    if OS != Os.WIN:
        return "npm"

    for d in os.environ.get("PATH").split(";"):
        if os.path.exists(f"{d}/npm"):
            return f"{d}/npm.cmd"


def assemble_build_dirs_frontend(versions: Versions):

    print("=======================================================")
    print("Building frontend")
    print(f"Frontend version: {versions.as_semver}")
    package_file = f"{FRONTEND_SRC_ROOT}/package.json"
    set_frontend_version(package_file, versions)

    with pushd(FRONTEND_SRC_ROOT):
        run_checked(f"{npm_cmd()} install")
        run_checked(f"{npm_cmd()} run build-render")

    print("=======================================================")
    print(f"Copying frontend files into {BUILD_TMP}/static_file_server ... ")

    copy_tree(f"{FRONTEND_SRC_ROOT}/static_file_server/static_file_server" , f"{BUILD_TMP}/static_file_server", update=True)
    copy_tree(f"{FRONTEND_SRC_ROOT}/src/dist", f"{BUILD_TMP}/static_file_server/dist", update=True)


def build_wheel():

    print("=======================================================")
    print("Building the kernel")
    with pushd(BUILD_TMP):
        run_checked("python setup.py build_ext bdist_wheel")

    # ----- Set up the output ----
    rm_rf(BUILD_OUT)
    os.rename(f"{BUILD_TMP}/dist", BUILD_OUT)


def test_wheel():
    wheelname = glob.glob(f"{BUILD_OUT}/*.whl")[0]

    # ----- Test installation ----
    run(f"pip uninstall -y perceptilabs")
    run_checked(f"pip install {wheelname}")
    run_checked_arr(["python", "-c", "import perceptilabs"])


def run_lint_test():
    print("running pylint")
    with included_files_common() as ifc:
        with pushd(PROJECT_ROOT):
            run_checked(f"python {SCRIPTS_DIR}/test_pylint.py {ifc}")


def run_cython_test():
    print("Running cython tests")
    with pushd(BUILD_TMP):
        run_checked("python setup.py test_cythonize")


def run_pytest_tests():
    print("Running python tests")
    with pushd(BACKEND_SRC):
        run_checked("python -m pytest")

def run_django_tests():
    print("Running django tests")
    with pushd(FILESERVER_DIR):
        subprocess.run([PYTHON, "-m", "django", "test", "--settings", "fileserver.settings"])

def which_cmd():
    if OS == Os.WIN:
        return "where"
    else:
        return "which"


def print_environment():
    print("=======================================================")
    print("Environment: ")
    print("Python location: " + get_run_checked(f"{which_cmd()} python"))
    print("node.js version: " + get_run_checked("node --version"))
    print("npm version: " + get_run_checked(f"{npm_cmd()} --version"))

    print("Pip list:")
    run_checked("pip list")

def assemble_package_datas(sources, dest):
    import json
    def load_json(filename):
        print(filename)
        with open(filename, "r") as f:
            return json.load(f)

    def dump_json(d, filename):
        with open(filename, "w") as f:
            json.dump(d, f, indent=2)

    def merge_dicts(dicts):
        ret = {}
        for d in dicts:
            ret = {**ret, **d}
        return ret;

    source_files = [f"{PROJECT_ROOT}/{s}/package_data.json" for s in sources]
    dicts = [load_json(f) for f in source_files]
    joined = merge_dicts(dicts)
    print(joined)
    dump_json(joined, dest)
    pass

def combine_files(sources, dest):
    with open(dest, "w") as dest_f:
        for source in sources:
            with open(source, "r") as source_f:
                lines = source_f.readlines()
                dest_f.writelines(lines)

def combine_requirements_files(roots, dest):
    requirements_files = [f"{PROJECT_ROOT}/{d}/requirements.txt" for d in roots]
    combine_files(requirements_files, dest)

def wheel():
    assert_python_version()
    install_prereqs()
    print_environment()
    version = calc_version()

    mkdir_p(BUILD_TMP)
    assemble_build_dirs_frontend(version)
    train_models()
    copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_TMP}/licenses/", update=True)
    copy_files(f"{PROJECT_ROOT}/backend", BUILD_TMP, list_path= f"{PROJECT_ROOT}/backend/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/rygg", BUILD_TMP,  list_path=f"{PROJECT_ROOT}/rygg/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/fileserver", BUILD_TMP,  list_path=f"{PROJECT_ROOT}/fileserver/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/perceptilabs_runner", f"{BUILD_TMP}/perceptilabs_runner/",  list_path=f"{PROJECT_ROOT}/perceptilabs_runner/included_files.txt")
    copy_file(f"{WHEELFILES_DIR}/setup.cfg", f"{BUILD_TMP}/setup.cfg", update=True)
    combine_requirements_files("backend rygg fileserver".split(), f"{BUILD_TMP}/requirements.txt")
    copy_file(f"{SCRIPTS_DIR}/setup.py", f"{BUILD_TMP}/setup.py", update=True)
    assemble_package_datas(
            ["backend", "rygg", "fileserver", "frontend", "perceptilabs_runner"],
           f"{BUILD_TMP}/package_data.json")
    write_all_lines(f"{BUILD_TMP}/cython_roots.txt", ["perceptilabs\n", "rygg\n", "fileserver\n", "static_file_server\n"])
    with included_files_common() as inc:
        copy_file(inc, f"{BUILD_TMP}/included_files.txt", update=True)

    set_wheel_version(version)
    name = get_wheel_name()
    set_wheel_name(name)
    build_wheel()
    test_wheel()


def test():
    assert_python_version()
    install_prereqs()
    print_environment()

    train_models()

    mkdir_p(BUILD_TMP)
    copy_files(f"{PROJECT_ROOT}/backend", BUILD_TMP, list_path= f"{PROJECT_ROOT}/backend/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/rygg", BUILD_TMP,  list_path=f"{PROJECT_ROOT}/rygg/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/fileserver", BUILD_TMP,  list_path=f"{PROJECT_ROOT}/fileserver/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/perceptilabs_runner", f"{BUILD_TMP}/perceptilabs_runner/",  list_path=f"{PROJECT_ROOT}/perceptilabs_runner/included_files.txt")
    combine_requirements_files("backend rygg fileserver".split(), f"{BUILD_TMP}/requirements.txt")
    copy_file(f"{SCRIPTS_DIR}/setup.py", f"{BUILD_TMP}/setup.py", update=True)
    write_all_lines(f"{BUILD_TMP}/cython_roots.txt", ["perceptilabs\n", "rygg\n", "fileserver\n", "static_file_server\n"])
    run_lint_test()
    run_cython_test()
    run_pytest_tests()
    run_django_tests()

class DockerBuilder():
    @staticmethod
    def assembleKernel():
        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_kernel_docker(versionString)

    @staticmethod
    def assembleFrontend():
        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_frontend_docker(versionString)

    @staticmethod
    def assembleRygg():
        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_rygg_docker(versionString)

    @staticmethod
    def build():
        build_kernel()
        build_frontend()
        build_rygg()

    @staticmethod
    def _set_dockerfile_version_label(rootDir, versions: Versions):
        dockerfile = f"{rootDir}/Dockerfile"
        sed_i(dockerfile, "version *=\".*\"", f"version=\"{versions.as_pep440}\"")

    @staticmethod
    def _assemble_kernel_docker(versions: Versions):
        copy_tree(f"{BACKEND_SRC}/", f"{BUILD_DOCKER_KERNEL}", update=True)
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_KERNEL}/licenses/", update=True)
        copy_file(f"{SCRIPTS_DIR}/setup.py", f"{BUILD_DOCKER_KERNEL}/setup.py", update=True)
        copy_file(f"{SCRIPTS_DIR}/requirements_build.txt", f"{BUILD_DOCKER_KERNEL}/requirements_build.txt", update=True)
        FILES_FROM_DOCKER_DIR = "setup.cfg entrypoint.sh Dockerfile".split()
        for from_docker in FILES_FROM_DOCKER_DIR:
            copy_file( f"{PROJECT_ROOT}/docker/kernel/{from_docker}", f"{BUILD_DOCKER_KERNEL}/{from_docker}", update=True)
        write_all_lines(f"{BUILD_DOCKER_KERNEL}/cython_roots.txt", ["perceptilabs\n"])

        DockerBuilder._set_dockerfile_version_label(BUILD_DOCKER_KERNEL, versions)
        set_perceptilabs_inner_version(BUILD_DOCKER_KERNEL, versions)
        write_version_file(BUILD_DOCKER_KERNEL, versions)


    @staticmethod
    def _assemble_frontend_docker(versions: Versions):
        copy_tree(f"{FRONTEND_SRC_ROOT}/", BUILD_DOCKER_FRONTEND, update=True)
        rm_rf(f"{BUILD_DOCKER_FRONTEND}/node_modules")
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_FRONTEND}/licenses/", update=True)

        FILES_FROM_DOCKER_DIR = "Dockerfile http.conf run-httpd.sh".split()
        for from_docker in FILES_FROM_DOCKER_DIR:
            copy_file(f"{PROJECT_ROOT}/docker/Frontend/{from_docker}", f"{BUILD_DOCKER_FRONTEND}/{from_docker}", update=True)

        #TODO: this is a terrible hack to turn off autosuggest for docker
        # the real fix is tracked in bug 895 and story 896
        cfgfile = f"{BUILD_DOCKER_FRONTEND}/src/config/prod.env.js"
        sed_i(cfgfile, ".*FORCE_DEFAULT_PROJECT:.*", f"FORCE_DEFAULT_PROJECT: '\"false\"'")
        sed_i(cfgfile, ".*FORCE_DEFAULT_PROJECT:.*,", f"FORCE_DEFAULT_PROJECT: '\"false\"',")

        DockerBuilder._set_dockerfile_version_label(BUILD_DOCKER_FRONTEND, versions)
        set_frontend_version(f"{BUILD_DOCKER_FRONTEND}/package.json", versions)


    @staticmethod
    def _assemble_rygg_docker(versions: Versions):
        copy_tree(f"{RYGG_DIR}/", f"{BUILD_DOCKER_RYGG}", update=True)
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_RYGG}/licenses/", update=True)
        set_rygg_inner_version(BUILD_DOCKER_RYGG, versions)
        DockerBuilder._set_dockerfile_version_label(BUILD_DOCKER_RYGG, versions)


    @staticmethod
    def build_kernel():
        with pushd(BUILD_DOCKER_KERNEL):
            run_checked("docker build . --tag=kernel_dev")
        # TODO: run a sanity check on the kernel

    @staticmethod
    def build_frontend():
        with pushd(BUILD_DOCKER_FRONTEND):
            run_checked("docker build . --tag=frontend_dev")
        # TODO: run a sanity check on the frontend

    @staticmethod
    def build_rygg():
        with pushd(BUILD_DOCKER_RYGG):
            run_checked("docker build . --tag=rygg_dev")
        # TODO: get rygg to build with obfuscation like the kernel does
        # TODO: run a sanity check on rygg


def clean():
    rm_rf(BUILD_DIR)

if __name__ == "__main__":
    USAGE = f"USAGE: {__file__} (clean|wheel|test|docker (kernel|frontend|rygg))"

    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    build_type = sys.argv[1]
    if build_type == "clean":
        clean()
    elif build_type == "wheel":
        wheel()
    elif build_type == "test":
        test()
    elif build_type == "docker":
        install_docker_host_prereqs()
        if len(sys.argv) < 3:
            print(USAGE)
            sys.exit(1)
        dockertype = sys.argv[2]
        if dockertype == "kernel":
            DockerBuilder.assembleKernel()
        elif dockertype == "frontend":
            DockerBuilder.assembleFrontend()
        elif dockertype == "rygg":
            DockerBuilder.assembleRygg()
        else:
            print(f"Invalid docker type: {dockertype}")
            print(USAGE)
            sys.exit(1)
        print(f"\nTo run the docker build. cd into build/docker/{dockertype} and run `docker build .`")
    else:
        print(f"Invalid build type: {build_type}")
        print(USAGE)
        sys.exit(1)
