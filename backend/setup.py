import os
import glob
from Cython.Build import cythonize
from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py as _build_py


included_files = glob.glob('perceptilabs/**/*.py', recursive=True)


cy_extensions = []
for path in included_files:
    if path.endswith('__init__.py') or path.endswith('__main__.py'):
        continue
    
    module = path.replace(os.path.sep, '.')[:-3]        
    ext = Extension(module, [path])
    cy_extensions.append(ext)
    print(f"Created cython extension for module {module} [{path}]")
        

        
class build_py(_build_py):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)

        kept_modules = []
        for pkg, mod, file_ in modules:
            if file_.endswith('__init__.py') or file_.endswith('__main__.py'):
                kept_modules.append((pkg, mod, file_))
                
        return kept_modules
                                    
setup(
    name='perceptilabs',
    version='0.1.0',
    packages=find_packages(),
    package_data={
        'perceptilabs': [
            '*.json',
            'insights/csv_ram_estimator/*.csv',
            'script/templates/*.j2'
        ],
    },
    ext_modules=cythonize(cy_extensions),
    cmdclass = {'build_py': build_py},    
)

