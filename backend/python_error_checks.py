def test_pylint():
    from pylint import epylint as lint

    with open('../scripts/included_files.txt') as f:
        for line in f:
            if "#" not in line and line.strip():
                print("Checking %s" % line.strip())
                lint.py_run(line.strip() + " -E --exit-zero")

def test_cython():
    import sys, os
    from setuptools import setup, find_packages, Extension
    from Cython.Build import cythonize
    from distutils.command import build_ext

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
            [extPath]
            )

    extNames = scandir("")

    extensions = [makeExtension(name) for name in extNames]

    try:
        setup(name='tests',
            ext_modules=cythonize(extensions))
    except:
        raise
    finally:
        exit(2)

if __name__ == "__main__":
    test_pylint()
    test_cython()