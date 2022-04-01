#!/usr/bin/env python

from contextlib import contextmanager
from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
from enum import Enum, auto
from shutil import rmtree, move
from subprocess import Popen, PIPE, CalledProcessError
from urllib.parse import urlparse
import glob
import os
import re
import socket
import subprocess
import sys
import tempfile
import time

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
VALID_PYTHON_VERSION_PATTERN = "python 3\.[678][^\d]"

# this depends on pwd being in the scripts directory
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
BACKEND_SRC = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_SRC_ROOT = os.path.join(PROJECT_ROOT, "frontend")
RYGG_DIR = os.path.join(PROJECT_ROOT, "rygg")
MONITOR_DIR = os.path.join(PROJECT_ROOT, "monitor")
WHEELFILES_DIR = os.path.join(PROJECT_ROOT, "wheelfiles")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
BUILD_TMP = os.path.join(BUILD_DIR, "tmp")
BUILD_OUT = os.path.join(BUILD_DIR, "out")

BUILD_DOCKER = os.path.join(BUILD_DIR, "docker")
BUILD_DOCKER_COMPOSE = os.path.join(BUILD_DOCKER, "compose")
BUILD_DOCKER_FRONTEND = os.path.join(BUILD_DOCKER, "frontend")
BUILD_DOCKER_FRONTEND_STATIC_FILESERVER = os.path.join(BUILD_DOCKER_FRONTEND, "static_file_server")
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

@contextmanager
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
        if os.path.isdir(dirname):
            rmtree(dirname)
        else:
            os.remove(dirname)


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

def run_checked_arr(arr, **popen_kwargs):
    kwargs = {
        "stdout": PIPE,
        "bufsize": 1,
        "universal_newlines": True,
        **popen_kwargs
    }
    with Popen(arr, **kwargs) as p:
        for line in p.stdout:
            print(line, end="")  # process line here

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)


def run_checked(cmd, **popen_kwargs):
    print(f"$ {cmd}")
    as_arr = cmd.split()
    run_checked_arr(as_arr, **popen_kwargs)


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

@contextmanager
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

    run_checked(f"pip install -r {BACKEND_SRC}/requirements.txt")
    run_checked(f"pip install -r {RYGG_DIR}/requirements.txt")
    run_unchecked("pip install -r requirements_build.txt")

def install_docker_host_prereqs():
    run_unchecked("pip install --upgrade pip")
    run_unchecked("pip install semver>=2.10 packaging>=20.4")


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


def set_staticfileserver_inner_version(rootDir, versions: Versions):
    init_py = os.path.join(rootDir, "static_file_server", "__init__.py")
    sed_i(init_py, "^__version__ *=.*", f"__version__='{versions.as_pep440}'")


def set_rygg_inner_version(rootDir, versions: Versions):
    init_py = os.path.join(rootDir, "rygg", "__init__.py")
    sed_i(init_py, "^__version__ *=.*", f"__version__='{versions.as_pep440}'")

def set_monitor_inner_version(rootDir, versions: Versions):
    init_py = os.path.join(rootDir, "monitor", "__init__.py")
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

def set_auth_env():
    print("Setting AUTH_ENV to 'prod'")
    sed_i(f"{BUILD_TMP}/rygg/settings.py", "^AUTH_ENV_DEFAULT.*$", "AUTH_ENV_DEFAULT='prod'")
    sed_i(f"{BUILD_TMP}/perceptilabs/settings.py", "^AUTH_ENV_DEFAULT.*$", "AUTH_ENV_DEFAULT='prod'")

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
        run_checked("python -m pytest -rfe -vv --log-cli-level=10 --capture=no")

def run_django_tests():
    print("Running django tests")
    env={"AUTH_ENV": '', **os.environ}
    with pushd(RYGG_DIR):
        run_checked_arr([PYTHON, "-m", "django", "test", "--settings", "rygg.settings"], env=env, stderr=subprocess.STDOUT)

def run_integration_tests():
    # Integration tests only work on linux since OSX and Win build agents can't run docker
    if OS != Os.LINUX:
        return

    redis_url = os.getenv("PL_REDIS_URL", "redis://127.0.0.1:6379")
    parsed_redis_url = urlparse(redis_url)
    redis_host = parsed_redis_url.hostname
    redis_port = parsed_redis_url.port

    def is_port_live(host, port):
        with socket.socket() as s:
            rc = s.connect_ex((host, port))
            return rc == 0

    def wait_for_port(host, port, interval_secs=1, timeout_secs=10):
        count = 0
        max_tries = timeout_secs / interval_secs
        while True:
            time.sleep(interval_secs)
            if is_port_live(host, port):
                return

            count += 1
            if count > max_tries:
                raise Exception(f"Timeout while waiting for port {port}")

    @contextmanager
    def popen_with_terminate(*args, **kwargs):
        with Popen(*args, **kwargs) as p:
            try:
                yield p
            finally:
                p.terminate()

    if not is_port_live(redis_host, redis_port):
        raise Exception("Redis needs to be running")


    upload_dir = tempfile.gettempdir()
    env={
        "PL_FILE_SERVING_TOKEN": "thetoken",
        "PL_TUTORIALS_DATA": os.path.join(BACKEND_SRC, "perceptilabs", "tutorial_data"),
        "PL_FILE_UPLOAD_DIR": upload_dir,
        "PERCEPTILABS_DB": os.path.join(os.getcwd(), "db.sqlite3"),
        "container": "any ol' string",
        **os.environ
    }
    integration_tests_path = os.path.join(RYGG_DIR, 'integration_tests')

    print("---------------------------------------------------------------------------------------------------")
    print("Running rygg integration tests")
    with Popen([PYTHON, "manage.py", "migrate"], cwd=RYGG_DIR, env=env) as migrator_proc:
        migrator_proc.wait(timeout=30)

    with popen_with_terminate([PYTHON, "manage.py", "runserver", "0.0.0.0:8000"], cwd=RYGG_DIR, env=env) as server_proc:
        wait_for_port('127.0.0.1', 8000, interval_secs=1)
        with popen_with_terminate(["celery", "-A", "rygg", "worker", "-l", "DEBUG", "--queues=rygg"], cwd=RYGG_DIR, env=env) as server_proc_c:
            run_checked_arr([PYTHON, "-m", "pytest", "--host", "localhost", "-vv"], cwd=integration_tests_path, env={**env, **os.environ})

    print("rygg integration tests passed")
    print("---------------------------------------------------------------------------------------------------")


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
                lines = [line.strip('\n') + '\n' for line in source_f.readlines()]
                print(lines)
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

    copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_TMP}/licenses/", update=True)
    copy_files(f"{PROJECT_ROOT}/backend", BUILD_TMP, list_path= f"{PROJECT_ROOT}/backend/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/rygg", BUILD_TMP,  list_path=f"{PROJECT_ROOT}/rygg/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/perceptilabs_runner", f"{BUILD_TMP}/perceptilabs_runner/",  list_path=f"{PROJECT_ROOT}/perceptilabs_runner/included_files.txt")
    copy_file(f"{WHEELFILES_DIR}/setup.cfg", f"{BUILD_TMP}/setup.cfg", update=True)
    combine_requirements_files("backend rygg frontend/static_file_server".split(), f"{BUILD_TMP}/requirements.txt")
    copy_file(f"{SCRIPTS_DIR}/setup.py", f"{BUILD_TMP}/setup.py", update=True)
    assemble_package_datas(
            ["backend", "rygg", "frontend", "perceptilabs_runner"],
           f"{BUILD_TMP}/package_data.json")
    write_all_lines(f"{BUILD_TMP}/cython_roots.txt", ["perceptilabs\n", "rygg\n", "static_file_server\n"])
    with included_files_common() as inc:
        copy_file(inc, f"{BUILD_TMP}/included_files.txt", update=True)

    set_wheel_version(version)
    name = get_wheel_name()
    set_wheel_name(name)
    set_auth_env()
    build_wheel()
    test_wheel()


def test():
    assert_python_version()
    install_prereqs()
    print_environment()

    mkdir_p(BUILD_TMP)
    copy_files(f"{PROJECT_ROOT}/backend", BUILD_TMP, list_path= f"{PROJECT_ROOT}/backend/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/rygg", BUILD_TMP,  list_path=f"{PROJECT_ROOT}/rygg/included_files.txt")
    copy_files(f"{PROJECT_ROOT}/perceptilabs_runner", f"{BUILD_TMP}/perceptilabs_runner/",  list_path=f"{PROJECT_ROOT}/perceptilabs_runner/included_files.txt")
    combine_requirements_files("backend rygg".split(), f"{BUILD_TMP}/requirements.txt")
    copy_file(f"{SCRIPTS_DIR}/setup.py", f"{BUILD_TMP}/setup.py", update=True)
    write_all_lines(f"{BUILD_TMP}/cython_roots.txt", ["perceptilabs\n", "rygg\n", "static_file_server\n"])
    run_pytest_tests()
    run_django_tests()
    run_integration_tests()
    run_lint_test()
    run_cython_test()



class DockerBuilder():
    @staticmethod
    def all(do_clean=False):
        DockerBuilder.assembleCompose(do_clean=do_clean)
        DockerBuilder.assembleKernel(do_clean=do_clean)
        DockerBuilder.assembleFrontend(do_clean=do_clean)
        DockerBuilder.assembleRygg(do_clean=do_clean)
        DockerBuilder.build_kernel()
        DockerBuilder.build_frontend()
        DockerBuilder.build_rygg()
        DockerBuilder.build_monitor()


    @staticmethod
    def assembleCompose(do_clean=False):
        if do_clean:
            rm_rf(BUILD_DOCKER_COMPOSE)

        mkdir_p(BUILD_DOCKER_COMPOSE)
        DockerBuilder._assemble_docker_compose()

    @staticmethod
    def assembleKernel(do_clean=False):
        if do_clean:
            rm_rf(BUILD_DOCKER_KERNEL)

        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_kernel_docker(versionString)

    @staticmethod
    def assembleFrontend(do_clean=False):
        if do_clean:
            rm_rf(BUILD_DOCKER_FRONTEND)

        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_frontend_docker(versionString)

    @staticmethod
    def assembleRygg(do_clean=False):
        if do_clean:
            rm_rf(BUILD_DOCKER_RYGG)

        mkdir_p(BUILD_DOCKER)
        versionString = calc_version()
        DockerBuilder._assemble_rygg_docker(versionString)

    @staticmethod
    def _set_dockerfile_version_label(rootDir, versions: Versions):
        dockerfile = f"{rootDir}/Dockerfile"
        sed_i(dockerfile, "version *=\".*\"", f"version=\"{versions.as_pep440}\"")

    @staticmethod
    def _append_to(src_file, dest_file):
        with open(src_file, "r") as src,\
             open(dest_file, "a") as dest:
                 dest.write(src.read())

    @staticmethod
    def _assemble_docker_compose():
        copy_tree(f"{PROJECT_ROOT}/docker/compose/system_migrations/", f"{BUILD_DOCKER_COMPOSE}/system_migrations/", update=True)
        copy_file(f"{PROJECT_ROOT}/docker/compose/install_perceptilabs_enterprise", f"{BUILD_DOCKER_COMPOSE}", update=True)


    @staticmethod
    def _assemble_kernel_docker(versions: Versions):
        rm_rf(f"{BACKEND_SRC}/upstream")
        rm_rf(f"{BACKEND_SRC}/downstream")
        copy_tree(f"{BACKEND_SRC}/", f"{BUILD_DOCKER_KERNEL}", update=True)
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_KERNEL}/licenses/", update=True)
        copy_file(f"{SCRIPTS_DIR}/setup.py", f"{BUILD_DOCKER_KERNEL}/setup.py", update=True)
        copy_file(f"{SCRIPTS_DIR}/requirements_build.txt", f"{BUILD_DOCKER_KERNEL}/requirements_build.txt", update=True)

        FILES_FROM_DOCKER_DIR = "setup.cfg entrypoint.sh Dockerfile".split()
        for from_docker in FILES_FROM_DOCKER_DIR:
            copy_file( f"{PROJECT_ROOT}/docker/kernel/{from_docker}", f"{BUILD_DOCKER_KERNEL}/{from_docker}", update=True)
        set_perceptilabs_inner_version(BUILD_DOCKER_KERNEL, versions)
        sed_i(f"{BUILD_DOCKER_KERNEL}/requirements.txt", "^opencv-python.*$", "opencv-python-headless")


        write_all_lines(f"{BUILD_DOCKER_KERNEL}/cython_roots.txt", ["perceptilabs\n"])

        DockerBuilder._set_dockerfile_version_label(BUILD_DOCKER_KERNEL, versions)
        write_version_file(BUILD_DOCKER_KERNEL, versions)


    @staticmethod
    def _assemble_frontend_docker(versions: Versions):
        copy_files(f"{FRONTEND_SRC_ROOT}/", BUILD_DOCKER_FRONTEND, list_path=f"{FRONTEND_SRC_ROOT}/included_files.txt")
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_FRONTEND}/licenses/", update=True)

        FILES_FROM_DOCKER_DIR = "Dockerfile http.conf run-httpd.sh .dockerignore".split()
        for from_docker in FILES_FROM_DOCKER_DIR:
            copy_file(f"{PROJECT_ROOT}/docker/Frontend/{from_docker}", f"{BUILD_DOCKER_FRONTEND}/{from_docker}", update=True)

        set_staticfileserver_inner_version(BUILD_DOCKER_FRONTEND_STATIC_FILESERVER, versions)
        DockerBuilder._set_dockerfile_version_label(BUILD_DOCKER_FRONTEND, versions)
        set_frontend_version(f"{BUILD_DOCKER_FRONTEND}/package.json", versions)



    @staticmethod
    def _assemble_rygg_docker(versions: Versions):
        copy_files(f"{RYGG_DIR}/", f"{BUILD_DOCKER_RYGG}", list_path=f"{RYGG_DIR}/included_files.txt")
        copy_file(f"{RYGG_DIR}/requirements.txt", f"{BUILD_DOCKER_RYGG}/requirements.txt", update=True)
        copy_file(f"{RYGG_DIR}/start.sh", f"{BUILD_DOCKER_RYGG}/start.sh", update=True)
        copy_file(f"{RYGG_DIR}/wait-for-db.py", f"{BUILD_DOCKER_RYGG}/wait-for-db.py", update=True)
        copy_file(f"{RYGG_DIR}/Dockerfile", f"{BUILD_DOCKER_RYGG}/Dockerfile", update=True)
        copy_tree(f"{PROJECT_ROOT}/licenses/", f"{BUILD_DOCKER_RYGG}/licenses/", update=True)
        set_rygg_inner_version(BUILD_DOCKER_RYGG, versions)
        DockerBuilder._set_dockerfile_version_label(BUILD_DOCKER_RYGG, versions)


    @staticmethod
    def build_kernel():
        with pushd(BUILD_DOCKER_KERNEL):
            run_checked("docker build . --tag=dev/kernel:latest")
        # TODO: run a sanity check on the kernel

    @staticmethod
    def build_frontend():
        with pushd(BUILD_DOCKER_FRONTEND):
            run_checked("docker build . --tag=dev/frontend:latest")
        # TODO: run a sanity check on the frontend

    @staticmethod
    def build_rygg():
        with pushd(BUILD_DOCKER_RYGG):
            run_checked("docker build . --tag=dev/rygg:latest")
        # TODO: run a sanity check on rygg

    @staticmethod
    def build_monitor():
        with pushd(MONITOR_DIR):
            versionString = calc_version().as_pep440
            run_checked(f"docker build . --tag=dev/monitor:latest --build-arg VERSION={versionString}")

            # Sanity-check the image
            py_script = f"import monitor; assert monitor.__version__ == \"{versionString}\";"
            run_checked_arr(["docker", "run", "-it", "--rm", "dev/monitor:latest", "python", "-c", py_script])

def clean():
    rm_rf(BUILD_DIR)

if __name__ == "__main__":
    USAGE = f"USAGE: {__file__} (clean|wheel|test|docker (kernel|frontend|rygg|all|compose))"

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

        do_clean = ('--clean' in sys.argv)

        dockertype = sys.argv[2]
        if dockertype == "compose":
            DockerBuilder.assembleCompose(do_clean=do_clean)
        elif dockertype == "kernel":
            DockerBuilder.assembleKernel(do_clean=do_clean)
        elif dockertype == "frontend":
            DockerBuilder.assembleFrontend(do_clean=do_clean)
        elif dockertype == "rygg":
            DockerBuilder.assembleRygg(do_clean=do_clean)
        elif dockertype == "monitor":
            DockerBuilder.build_monitor()
        elif dockertype == "all":
            DockerBuilder.all(do_clean=do_clean)
        else:
            print(f"Invalid docker type: {dockertype}")
            print(USAGE)
            sys.exit(1)

        if not dockertype in ["all", "compose", "monitor"]:
            print(f"\nTo run the docker build. cd into build/docker/{dockertype} and run `docker build .`")
    else:
        print(f"Invalid build type: {build_type}")
        print(USAGE)
        sys.exit(1)
