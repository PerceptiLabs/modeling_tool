from setuptools import setup
from Cython.Build import cythonize

setup(name='tests',
      ext_modules=cythonize("*.py"))