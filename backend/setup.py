from setuptools import setup
from Cython.Build import cythonize
from distutils.command import build_ext

# def get_export_symbols(self, ext):
#     parts = ext.name.split(".")
#     if parts[-1] == "__init__":
#         initfunc_name = "PyInit_" + parts[-2]
#     else:
#         initfunc_name = "PyInit_" + parts[-1]


# build_ext.build_ext.get_export_symbols = get_export_symbols

# targets = ['*.py', 'analytics/*.py', 'core_new/*.py', 'core_new/data/*.py', 'code_generator/*.py']
targets = ['*.py']

setup(name='tests',
      ext_modules=cythonize(targets))
