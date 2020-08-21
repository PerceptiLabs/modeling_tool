import os
import requests
import json
from rygg import __version__ as current_version_str
from packaging.version import parse as parse_version


def get_newer_versions():
    pass

def get_pypi_info():
    try:
        return requests.get("https://pypi.org/pypi/perceptilabs/json").text
    except:
        return None

def pypi_versions():
    pypi_info = get_pypi_info()
    as_dict = json.loads(pypi_info)
    version_strings = as_dict['releases'].keys()
    return [parse_version(s) for s in version_strings]

def updates_available():
    # if the distribution is docker, then don't upgrade from there
    if os.path.isfile("/.dockerenv"):
        return []

    versions = pypi_versions()
    print(versions)

    current_version = parse_version(current_version_str)

    # If the version isn't on pypi, then it's not a distribution from there. Don't upgrade from there.
    if not any([v == current_version for v in versions]):
        return []

    return list([str(v) for v in versions if v > current_version])

