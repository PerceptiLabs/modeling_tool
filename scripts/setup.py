import os
import re
import glob
import sys
import pathlib
import traceback
from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.install import install
from setuptools import Command
from subprocess import check_call

# setuptools wants be imported before distutils, which is pulled in by cython
from Cython.Build import cythonize

def get_requirements(thisfile):
    def relative_file(thisfile, name):
        dirname = pathlib.Path(thisfile).parent.absolute()
        print(dirname)
        requirements_path = os.path.join(dirname, name)
        print(requirements_path)
        return requirements_path

    requirements = [
        l.strip() for l in open(relative_file(thisfile, "requirements.txt"))
    ]
    return list(requirements)


def get_all_cythonized_modules():
    def is_compilable(filename):
        # if a directory ends with .py for some reason, skip it
        if not os.path.isfile(filename):
            print(f"Skipping non-file with a .py extension: {filename}")
            return False

        # Don't compile plumbing files
        if filename.endswith("__init__.py") or filename.endswith("__main__.py"):
            return False

        # migrations don't cythonize
        if re.match(".*migrations.\d+.*", filename):
            print(f"Skipping migration {filename}")
            return False

        # don't check myself
        if __file__.endswith(filename):
            print("Skipping the test file")
            return False

        return True

    def make_extension(path):
        module = path.replace(os.path.sep, ".")[:-3]
        return Extension(module, [path])

    def get_modules_to_cythonize(root):
        py_files = glob.glob(f"{root}/**/*.py", recursive=True)
        ret_iter = [py_file for py_file in py_files if is_compilable(py_file)]
        ret = list(ret_iter)
        print(f"In {root} Found these python modules to include: {ret}")
        return ret

    def get_all_modules_to_cythonize():
        cython_roots = [l.strip() for l in open("cython_roots.txt")]

        return [
            module for root in cython_roots for module in get_modules_to_cythonize(root)
        ]

    def get_all_cy_extensions():
        return [make_extension(module) for module in get_all_modules_to_cythonize()]

    extensions = list(get_all_cy_extensions())
    ret = cythonize(extensions, compiler_directives={"language_level": 2})
    return ret


class build_py(_build_py):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)

        kept_modules = []
        for pkg, mod, file_ in modules:
            if file_.endswith("__init__.py") or file_.endswith("__main__.py"):
                kept_modules.append((pkg, mod, file_))
        return kept_modules


def load_json(filename):
    import json

    if not os.path.exists(filename):
        return {}

    with open(filename, "r") as f:
        return json.load(f)


def get_setupargs():
    ret = {
        "license": "Custom Proprietary License",
        "packages": find_packages(),
        "author": "PerceptiLabs",
        "author_email": "contact@perceptilabs.com",
        "url": "https://perceptilabs.com",
        "description": "",
        "long_description": "",
        "install_requires": get_requirements(__file__),
        "python_requires": ">=3.6,<3.9",
        "package_data": {},
        "ext_modules": get_all_cythonized_modules(),
        "cmdclass": {"build_py": build_py, "test_cythonize": CythonTestCommand,},
        "scripts": [],
    }

    package_data = load_json("package_data.json")
    if package_data:
        ret["package_data"] = package_data

    return ret


class CythonTestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            get_all_cythonized_modules()
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            exit(2)


if __name__ == "__main__":
    setup(**get_setupargs())
