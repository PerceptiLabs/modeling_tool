from setuptools import setup
from Cython.Build import cythonize

targets = ['*.py']

setup(name='tests',
      ext_modules=cythonize(targets))
