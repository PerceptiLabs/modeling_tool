# build using python setup.py build_ext bdist_wheel from backend/

import os
import glob
from setuptools import setup, find_packages
from Cython.Build import cythonize
from Cython.Distutils import build_ext

cython_targets = [
    x for x in glob.glob('perceptilabs' + '/**/*.py', recursive=True) 
    if 'test_' not in x
]

class MyBuildExt(build_ext):
    EXCLUDE_EXTENSIONS = ['.py', '.c']
    
    def run(self):
        build_dir = os.path.realpath(self.build_lib)
        
        paths = [f for f in glob.glob(build_dir + "/**/test_*", recursive=True)]
        for p in paths:
            os.remove(p)
        
        super().run()

        for ext in self.EXCLUDE_EXTENSIONS:
            paths = [f for f in glob.glob(build_dir + "/**/*" + ext, recursive=True)]
            for p in paths:
                os.remove(p)
                
setup(
    name='perceptilabs',
    version='0.1.0',
    packages=['perceptilabs'],
    package_data={'perceptilabs': ['code/templates/*.j2']},
    include_package_data=True,
    #install_requires=[
    #    'numpy',                     
    #],
    ext_modules=cythonize(cython_targets),
    cmdclass = {'build_ext': MyBuildExt},
)
