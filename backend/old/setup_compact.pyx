import sys, os
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
from distutils.command import build_ext

# targets = ['*.py']

# setup(name='tests',
#       ext_modules=cythonize(targets))

#def get_export_symbols(self, ext):
#    parts = ext.name.split(".")
#    if parts[-1] == "__init__":
#        initfunc_name = "PyInit_" + parts[-2]
#    else:
#        initfunc_name = "PyInit_" + parts[-1]

#build_ext.build_ext.get_export_symbols = get_export_symbols


def scandir(dir, files=[]):
    if dir:
        folder = os.listdir(dir)
    else:
        folder = os.listdir()
    for file in folder:
        path = os.path.join(dir, file)
        if os.path.isfile(path) and path.endswith(".py"):
            files.append(path.replace(os.path.sep, ".")[:-3])
        elif os.path.isdir(path):
            scandir(path, files)
    return files

def makeExtension(extName):
    extPath = extName.replace(".", os.path.sep)+".py"
    return Extension(
        extName,
        [extPath],
#        include_dirs = [libdvIncludeDir, "."],   # adding the '.' to include_dirs is CRUCIAL!!
        # extra_compile_args = ["-O3", "-Wall"],
        # extra_link_args = ['-g'],
        # libraries = ["dv",],
        )

extNames = scandir("")

extensions = [makeExtension(name) for name in extNames]

setup(name='test',
      ext_modules = cythonize(extensions),
     )
