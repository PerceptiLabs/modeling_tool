import os
import re
import glob
import sys
import pathlib
from Cython.Build import cythonize
from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.install import install
from subprocess import check_call

REQUIREMENTS_FILENAMES = [
    "requirements_wheel_docker.txt",
]

ROOTS = [
        "perceptilabs",
]

def relative_file(thisfile, name):
    dirname = pathlib.Path(thisfile).parent.absolute()
    print(dirname)
    requirements_path = os.path.join(dirname, name)
    print(requirements_path)
    return requirements_path


def get_requirements(thisfile):
    requirements = [
        l.strip()
        for name in REQUIREMENTS_FILENAMES
        for l in open(relative_file(thisfile, name))
    ]
    return list(requirements)


def is_special(path):
    return path.endswith("__init__.py") or path.endswith("__main__.py")
def is_migration(path):
    return re.match(".*\/\d{4}_.*.py", path) is not None


def make_extension(path):
    module = path.replace(os.path.sep, ".")[:-3]
    return Extension(module, [path])



def get_modules_to_cythonize(root):
    py_files = glob.glob(f"{root}/**/*.py", recursive=True)
    tmp = [f for f in py_files if not is_special(f)]
    included_files = [f for f in tmp if not is_migration(f)]
    ret = list(included_files)
    print("Found these python modules to include: " + str(included_files))
    return ret


def get_all_modules_to_cythonize():
    return [module for root in ROOTS for module in get_modules_to_cythonize(root)]


def get_all_cy_extensions():
    return [make_extension(module) for module in get_all_modules_to_cythonize()]


class build_py(_build_py):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)

        kept_modules = []
        for pkg, mod, file_ in modules:
            if file_.endswith("__init__.py") or file_.endswith("__main__.py"):
                kept_modules.append((pkg, mod, file_))

        return kept_modules


setup(
    name="perceptilabs",
    version="0.1.1",
    license="Custom Proprietary License",
    packages=find_packages(),
    author="PerceptiLabs",
    author_email="contact@perceptilabs.com",
    url="https://perceptilabs.com",
    description="",
    long_description="",
    install_requires=get_requirements(__file__),
    dependency_links=[
        'git+https://github.com/Kojoley/atari-py.git; platform_system == "Windows"',
    ],
    python_requires=">=3.6,<3.8",
    package_data={
        "perceptilabs": [
            "*.json",
            "insights/csv_ram_estimator/*.csv",
            "script/templates/*.j2",
            "core_new/layers/templates/*.j2",
            "tutorial_data/mnist_input.npy",
            "tutorial_data/mnist_labels.npy",
        ],
    },
    ext_modules=cythonize(cy_extensions),
    cmdclass={"build_py": build_py,},
)
