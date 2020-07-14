import sys, os
from setuptools import setup, Extension
from Cython.Build import cythonize
import traceback
import glob
import re

def makeExtension(filename):
    extName= filename.replace(os.path.sep, ".")[:-3]
    extPath = extName.replace(".", os.path.sep) + ".py"
    return Extension(extName, [extPath])

def is_compilable(filename):
    # if a directory ends with .py for some reason, skip it
    if not os.path.isfile(filename):
        print("Skipping non-file with a .py extension")
        return False

    # migrations don't cythonize
    if re.match(".*\/migrations\/\d+.*", filename):
        print("Skipping migration")
        return False

    # don't check myself
    if __file__.endswith(filename):
        print("Skipping the test file")
        return False

    return True


extensions = [makeExtension(py_file)
        for py_file
        in glob.glob("**/*.py", recursive=True)
        if is_compilable(py_file)]

modules = cythonize(extensions)

try:
    setup(name="tests", ext_modules=modules)
except Exception as e:
    print(e)
    traceback.print_tb(e.__traceback__)
    exit(2)

