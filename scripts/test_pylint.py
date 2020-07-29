import sys, os
from pylint import epylint as lint

args = sys.argv[1:]

if len(args) == 0:
    raise Exception(f"USAGE: {__file__} <path to included files>")

filename = args[0]

if not os.path.exists(filename):
    raise Exception(f"Files list '{filename}' doesn't exist")

with open(filename, mode="r") as f:
    for line in f:
        if "#" not in line and line.strip():
            print("Checking %s" % line.strip())
            lint.py_run(line.strip() + " -E --exit-zero")

