import contextlib
from enum import Enum, auto
import glob
import os
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
import sys
import re
from shutil import copyfile, rmtree, copytree


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


def copy_files(src_root, dest_root, list_path):
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
                copyfile(src, dest)
            elif os.path.isdir(src):
                dirname = os.path.dirname(dest)
                mkdir_p(dirname)
                copytree(src, dest)
            else:
                print(f"Skipping non-file: {src}")
                continue


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
    training_dir = os.path.join(
        BACKEND_SRC, "perceptilabs", "insights", "csv_ram_estimator"
    )
    with pushd(training_dir):
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


def calc_version():
    override = os.environ.get("PACKAGE_VERSION_OVERRIDE")
    if bool(override):
        return override

    with open(os.path.join(WHEELFILES_DIR, "version"), "r") as f:
        version = f.read().strip()
    # TODO: don't build knowledge of nightly builds into this script. Instead, build it into the pipeline
    if build_reason == "Schedule":
        version = f"{version}.{build_num}"
    print(f"version: {version}")
    return version


def set_wheel_version(version_string):
    print(f"setting wheel version to {version_string}")
    init_py = os.path.join(BUILD_TMP, "perceptilabs", "__init__.py")
    sed_i(init_py, "^__version__ *=.*", f"__version__='{version_string}'")

    setup_py = os.path.join(BUILD_TMP, "setup.py")
    sed_i(setup_py, "^VERSION_STRING *=.*$", f"VERSION_STRING='{version_string}'")


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
    sed_i(f"{BUILD_TMP}/setup.py", "^PACKAGE_NAME *=.*$", f"PACKAGE_NAME='{package_name}'")


# pull a directory under BUILD_TMP up a level
def hoist_directory(dirname):
    full_path = os.path.join(BUILD_TMP, dirname)
    if not os.path.exists(full_path):
        return
    to_remove = os.path.join(BUILD_TMP, "todo_remove")
    os.rename(full_path, to_remove)
    globname = os.path.join(to_remove, "*")
    for to_move in glob.glob(globname):
        dest = os.path.join(BUILD_TMP, os.path.basename(to_move))
        print(f"Moving {to_move} -> {dest}")
        os.rename(to_move, dest)
    rmtree(to_remove)


# PATH isn't obeyed correctly on windows
def npm_cmd():
    if OS != Os.WIN:
        return "npm"

    for d in os.environ.get("PATH").split(";"):
        if os.path.exists(f"{d}/npm"):
            return f"{d}/npm.cmd"


def build_frontend():
    print("=======================================================")
    print("Building frontend")
    with pushd(FRONTEND_SRC_ROOT):
        run_checked(f"{npm_cmd()} install")
        run_checked(f"{npm_cmd()} run build-render")


def assemble_build_dirs_common(build_type):
    rm_rf(BUILD_DIR)
    copy_files(PROJECT_ROOT, BUILD_TMP, f"{SCRIPTS_DIR}/included_files_common.txt")
    copy_files(
        PROJECT_ROOT, BUILD_TMP, f"{SCRIPTS_DIR}/included_files_{build_type}.txt"
    )
    print("hoisting dirs")
    hoist_directory("wheelfiles")
    hoist_directory("rygg")
    hoist_directory("backend")


def assemble_build_dirs_frontend():
    print("=======================================================")
    print(f"Copying frontend files into {BUILD_TMP}/static_file_server ... ")

    copytree(
        f"{FRONTEND_SRC_ROOT}/static_file_server/static_file_server",
        f"{BUILD_TMP}/static_file_server",
    )
    copytree(f"{FRONTEND_SRC_ROOT}/src/dist", f"{BUILD_TMP}/static_file_server/dist")


def build_wheel():

    print("=======================================================")
    print("Adding tutorial data to the output")
    # tutorial_files = "linreg_inputs linreg_outputs linreg_outputs_test mnist_input mnist_labels".split()
    # for filename in tutorial_files:
    copytree(
        f"{BACKEND_SRC}/perceptilabs/tutorial_data",
        f"{BUILD_TMP}/perceptilabs/tutorial_data",
    )

    print("=======================================================")
    print("Building the kernel")
    with pushd(BUILD_TMP):
        run_checked("python setup.py build_ext bdist_wheel")

    # ----- Set up the output ----
    os.rename(f"{BUILD_TMP}/dist", BUILD_OUT)


def test_wheel():
    wheelname = glob.glob(f"{BUILD_OUT}/*.whl")[0]

    # ----- Test installation ----
    run(f"pip uninstall -y perceptilabs")
    run_checked(f"pip install {wheelname}")
    run_checked_arr(["python", "-c", "import perceptilabs"])


def set_up_for_tests():
    print("Installing dependencies")
    run_checked("python -m pip install --upgrade pip setuptools")

    if OS == Os.WIN:
        run_unchecked('pip install "gym[atari]"')
        run_unchecked("pip install -r ../backend/requirements_windows.txt")
        run_unchecked("pip install pylint==2.4.3")
        run_unchecked("pip install pytest==5.3.1")
    else:
        run_checked(f"pip install -r {BACKEND_SRC}/requirements_posix_testing.txt")


def run_lint_test():
    print("running pylint")
    script = f"{SCRIPTS_DIR}/test_pylint.py"
    with pushd(PROJECT_ROOT):
        run_checked(f"python {script} {SCRIPTS_DIR}/included_files_common.txt")


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


def assemble_core_docker():
    copyfile(f"{PROJECT_ROOT}/Docker/Core/setup.py", f"{BUILD_TMP}/setup.py")
    # os.rename(f"{BUILD_TMP}/main.py", f"{BUILD_TMP}/main.pyx")
    for filename in glob.glob(f"{BUILD_TMP}/perceptilabs/**/__init__.py"):
        os.rename(filename, filename + "x")

    # --- do the compilation
    print("C compiling")
    with pushd(BUILD_TMP):
        run_checked("python setup.py build_ext --inplace --user")

    # Remove files so that they won't be copied to the container
    print("Cleaning up after the compilation")
    for filename in glob.glob(f"{BUILD_TMP}/perceptilabs/**/*.c"):
        os.remove(filename)
    for filename in glob.glob(f"{BUILD_TMP}/perceptilabs/**/*.py"):
        os.remove(filename)
    rmtree(f"{BUILD_TMP}/build")
    os.rename(f"{BUILD_TMP}/main.pyx", f"{BUILD_TMP}/main.py")
    for filename in glob.glob(f"{BUILD_TMP}/perceptilabs/**/__init__.pyx"):
        os.rename(filename, filename[0:-1])

    # Get the Docker-specific files in place for the docker build
    for filename in glob.glob(f"{PROJECT_ROOT}/Docker/Core/*"):
        copyfile(filename, f"{BUILD_TMP}/{filename}")


def maybe_build_core_docker():
    if not bool(os.environ.get("DO_DOCKER_BUILD")):
        print("You can now run docker build")
        return

    with pushd(BUILD_TMP):
        run_checked("docker build . --tag=core_quickcheck")
    run_checked("docker run -p 5000:5000 core_quickcheck")


def assemble_frontend_docker():
    frontend_tmp = os.path.join(BUILD_DIR, "frontend_out")
    for filename in glob.glob(f"{FRONTEND_SRC_ROOT}/src/dist/*"):
        copyfile(filename, f"{frontend_tmp}/{filename}")

    run_checked(f"ls -l -a {PROJECT_ROOT}/Docker/Frontend")
    for filename in glob.glob(f"{PROJECT_ROOT}/Docker/Frontend/*"):
        copyfile(filename, f"{frontend_tmp}/{filename}")


def wheel():
    assert_python_version()
    install_prereqs()
    print_environment()
    train_models()
    build_frontend()
    assemble_build_dirs_common("wheel")
    assemble_build_dirs_frontend()
    version = calc_version()
    set_wheel_version(version)
    name = get_wheel_name()
    set_wheel_name(name)
    build_wheel()
    test_wheel()


def test():
    assert_python_version()
    install_prereqs()
    set_up_for_tests()
    print_environment()
    train_models()
    assemble_build_dirs_common("test")
    run_lint_test()
    run_cython_test()
    run_pytest_tests()


def docker():
    assert_python_version()
    install_prereqs()
    print_environment()
    train_models()
    build_frontend()
    assemble_build_dirs_common("docker")
    assemble_core_docker()
    maybe_build_core_docker()
    assemble_frontend_docker()


if __name__ == "__main__":
    USAGE = f"USAGE: {__file__} (wheel|test|docker)"
    print(f"project root: {PROJECT_ROOT}")

    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    build_type = sys.argv[-1]
    if build_type == "wheel":
        wheel()
    elif build_type == "test":
        test()
    elif build_type == "docker":
        docker()
    else:
        print(f"Invalid build type: {build_type}")
        print(USAGE)
        sys.exit(1)
