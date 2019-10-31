from setuptools import setup
from Cython.Build import cythonize

targets = ['*.py', 'analytics/*.py', 'core_new/*.py', 'core_new/data/*.py', 'code_generator/*.py']

setup(name='tests',
      ext_modules=cythonize(targets))
