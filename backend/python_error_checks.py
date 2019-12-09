def test_pylint():
    from pylint import epylint as lint

    with open('../../scripts/included_files.txt') as f:
        for line in f:
            if "#" not in line and line.strip():
                print("Checking %s" % line.strip())
                lint.py_run(line.strip() + " -E --exit-zero")

def test_cython():
    from setuptools import setup
    from Cython.Build import cythonize
    from distutils.command import build_ext

    targets = ['*.py']

    setup(name='tests',
        ext_modules=targets)

if __name__ == "__main__":
    test_pylint()
    test_cython()