import os
import glob
from Cython.Build import cythonize
from setuptools import setup, Extension, find_packages
from setuptools.command.build_py import build_py as _build_py


included_files = glob.glob('perceptilabs/**/*.py', recursive=True)

# included_files = []
# with open('included_files.txt') as f:
#     for line in f:
#         tmp_line = line.strip()
#         if "#" not in tmp_line and tmp_line and tmp_line.endswith(".py"):
#             included_files.append(tmp_line)
#             # included_files.append(".".join(tmp_line.split(".")[:-1]).replace("/","."))

print("Found these python modules to include: " + str(included_files))


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
    author = 'PerceptiLabs',
    author_email = 'contact@perceptilabs.com',
    url = 'https://perceptilabs.com',
    description="",
    long_description="",
    install_requires=[
        'tensorflow-gpu == 1.13.1',
        'numpy >= 1.16.4',
        'fsspec >= 0.6.0',
        'pandas >= 0.25.0',
        'dask[array] >= 2.6.0',
        'websockets >= 8.1',
        'psutil >= 5.6.3',
        'scikit-image >= 0.15.0',
        'gym[atari]',
        'Jinja2 >= 2.10.3',
        'boltons >= 19.3.0',
        'scipy >= 1.3.0',
        'GPUtil >= 1.4.0',
        'sentry-sdk >= 0.10.2',
        'boto >= 2.49.0',
        'boto3 >= 1.9.233',
        'azure-storage >= 0.36.0',
        'astor >= 0.8.0',
        'cffi >= 1.13.2',
        'cryptography >= 2.8',
        'pycparser >= 2.19',
        'six >= 1.14.0',
        'scikit-learn >= 0.22.1',
    ],
    dependency_links=[
        'git+https://github.com/Kojoley/atari-py.git; platform_system == "Windows"',
    ],
    python_requires='>=3.6,<=3.7',
    package_data={
        'perceptilabs': [
            '*.json',
            'insights/csv_ram_estimator/*.csv',
            'script/templates/*.j2'
        ],
    },
    ext_modules=cythonize(cy_extensions),
    cmdclass={'build_py': build_py},    
)

