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
VALID_PYTHON_VERSION_PATTERN = "python 3\.[67][^\d]"

# this depends on pwd being in the scripts directory
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
BACKEND_SRC = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_SRC_ROOT = os.path.join(PROJECT_ROOT, "frontend")
RYGG_DIR = os.path.join(PROJECT_ROOT, "rygg")
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

def run_checked_arr(arr):
    with Popen(arr, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end="")  # process line here

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)


def run_checked(cmd):
    print(f"$ {cmd}")
    as_arr = cmd.split()
    run_checked_arr(as_arr)


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
    projects = "perceptilabs_runner rygg backend".split()
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
    with tempfile.NamedTemporaryFile(mode="w") as tmp:
        tmp.writelines(lines)
        tmp.flush()
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

    run_unchecked("pip install -r ../backend/requirements_build.txt")

def calc_version():
    # TODO: this variable from the pipeline shouldn't be buried so deep in the codebase
    override = os.environ.get("VERSION_OVERRIDE")
    if bool(override):
        return override

    with open(os.path.join(PROJECT_ROOT, "version"), "r") as f:
        version = f.read().strip()
    # TODO: don't build knowledge of nightly builds into this script. Instead, build it into the pipeline
    if build_reason == "Schedule":
        version = f"{version}.{build_num}"
    print(f"version: {version}")
    return version


def set_perceptilabs_inner_version(rootDir, versionString):
    init_py = os.path.join(rootDir, "perceptilabs", "__init__.py")
    sed_i(init_py, "^__version__ *=.*", f"__version__='{versionString}'")


def set_setup_version(rootDir, versionString):
    setup_py = os.path.join(rootDir, "setup.py")
    sed_i(setup_py, "^VERSION_STRING *=.*$", f"VERSION_STRING='{versionString}'")


def set_wheel_version(versionString):
    print(f"setting wheel version to {versionString}")
    set_perceptilabs_inner_version(BUILD_TMP, versionString)
    set_setup_version(BUILD_TMP, versionString)


def set_dockerfile_version_label(rootDir, versionString):
    dockerfile = f"{rootDir}/Dockerfile"
    sed_i(dockerfile, "version *=\".*\"", f"version=\"{versionString}\"")


def get_wheel_name():
    override = os.environ.get("PACKAGE_NAME_OVERRIDE")
    if bool(override):
        return override

    # TODO: don't build knowledge of nightly builds into this script. Instead, build it into the pipeline
    # for nightly builds, rename the package
    reason = os.environ.get("BUILD_REASON")
    if reason == "Schedule":
        return "perceptilabs-nightly"
    else:
        return "perceptilabs"


def set_wheel_name(package_name):
    sed_i( f"{BUILD_TMP}/setup.py", "^PACKAGE_NAME *=.*$", f"PACKAGE_NAME='{package_name}'")


# PATH isn't obeyed correctly on windows
def npm_cmd():
    if OS != Os.WIN:
        return "npm"

    for d in os.environ.get("PATH").split(";"):
        if os.path.exists(f"{d}/npm"):
            return f"{d}/npm.cmd"


def assemble_build_dirs_frontend():

    print("=======================================================")
    print("Building frontend")
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
        script = f"{SCRIPTS_DIR}/test_cython.py"
        # TODO: this fails. Do we keep it?
        run(f"python {script}")


def run_pytest_tests():
    print("Running python tests")
    cmd = "python -m pytest --capture=no"
    with pushd(BACKEND_SRC):
        # TODO: Windows tests fail. Get them working again
        if OS == Os.WIN:
            run_unchecked(cmd)
        else:
            run_checked(cmd)


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

def wheel():
    assert_python_version()
    install_prereqs()
    print_environment()

    mkdir_p(BUILD_TMP)
    assemble_build_dirs_frontend()
    train_models()
    copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_TMP}/licenses/", update=True)
    copy_files(f"{PROJECT_ROOT}/backend", BUILD_TMP, list_path= f"{PROJECT_ROOT}/backend/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/rygg", BUILD_TMP,  list_path=f"{PROJECT_ROOT}/rygg/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/perceptilabs_runner", f"{BUILD_TMP}/perceptilabs_runner/",  list_path=f"{PROJECT_ROOT}/perceptilabs_runner/included_files.txt")
    copy_file(f"{PROJECT_ROOT}/backend/requirements.txt", f"{BUILD_TMP}/requirements_wheel_backend.txt", update=True)
    copy_file(f"{PROJECT_ROOT}/rygg/requirements.txt", f"{BUILD_TMP}/requirements_wheel_rygg.txt", update=True)

    for f in ["setup.cfg", "setup.py"]:
        copy_file(f"{WHEELFILES_DIR}/{f}", f"{BUILD_TMP}/{f}", update=True)

    with included_files_common() as inc:
        copy_file(inc, f"{BUILD_TMP}/included_files.txt", update=True)

    version = calc_version()
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
    copy_files(f"{PROJECT_ROOT}/perceptilabs_runner", f"{BUILD_TMP}/perceptilabs_runner/",  list_path=f"{PROJECT_ROOT}/perceptilabs_runner/included_files.txt")
    run_lint_test()
    run_cython_test()
    run_pytest_tests()

class DockerBuilder():
    def assembleKernel():
        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_kernel_docker(versionString)

    def assembleFrontend():
        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_frontend_docker(versionString)

    def assembleRygg():
        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_rygg_docker(versionString)

    def build():
        build_kernel()
        build_frontend()
        build_rygg()

    def _assemble_kernel_docker(versionString):
        copy_tree(f"{BACKEND_SRC}/", f"{BUILD_DOCKER_KERNEL}", update=True)
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_KERNEL}/licenses/", update=True)
        FILES_FROM_DOCKER_DIR = "setup.py entrypoint.sh Dockerfile".split()
        for from_docker in FILES_FROM_DOCKER_DIR:
            copy_file( f"{PROJECT_ROOT}/docker/kernel/{from_docker}", f"{BUILD_DOCKER_KERNEL}/{from_docker}", update=True)

        set_dockerfile_version_label(BUILD_DOCKER_KERNEL, versionString)
        set_perceptilabs_inner_version(BUILD_DOCKER_KERNEL, versionString)
        set_setup_version(BUILD_DOCKER_KERNEL, versionString)


    def _assemble_frontend_docker(versionString):
        copy_tree(f"{FRONTEND_SRC_ROOT}/", BUILD_DOCKER_FRONTEND, update=True)
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_FRONTEND}/licenses/", update=True)

        FILES_FROM_DOCKER_DIR = "Dockerfile http.conf run-httpd.sh".split()
        for from_docker in FILES_FROM_DOCKER_DIR:
            copy_file(f"{PROJECT_ROOT}/docker/Frontend/{from_docker}", f"{BUILD_DOCKER_FRONTEND}/{from_docker}", update=True)

        set_dockerfile_version_label(BUILD_DOCKER_FRONTEND, versionString)
        #TODO: set version in package.json


    def _assemble_rygg_docker(versionString):
        copy_tree(f"{RYGG_DIR}/", f"{BUILD_DOCKER_RYGG}", update=True)
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_RYGG}/licenses/", update=True)
        set_dockerfile_version_label(BUILD_DOCKER_RYGG, versionString)


    def build_kernel():
        with pushd(BUILD_DOCKER_KERNEL):
            run_checked("docker build . --tag=kernel_dev")
        # TODO: run a sanity check on the kernel

    def build_frontend():
        with pushd(BUILD_DOCKER_FRONTEND):
            run_checked("docker build . --tag=frontend_dev")
        # TODO: run a sanity check on the frontend

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
