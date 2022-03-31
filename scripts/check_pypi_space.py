from debug_print import _d
import requests
import math
import sys

PROJECT = "perceptilabs"
API = f"https://pypi.org/pypi/{PROJECT}/json"
GB = 1024**3
MB = 1024**2
# _d(list(map(lambda x: round(x/MB, 1), release_sizes)))
ACCT_LIMIT = 10 * GB
SAFETY_CUSHION = 5  # save space for this many releases to be safe

response = requests.get("https://pypi.org/pypi/perceptilabs/json")
as_dict = response.json()
releases = as_dict.get("releases", {})
release_sizes = {
    k: sum(map(lambda file: file.get("size", 0), files))
    for k, files in releases.items()
}
if "-v" in sys.argv:
    for version, bytes in release_sizes.items():
        print(f"{version} : {math.floor(bytes / MB)}")

# releases = [release for release in as_dict.get("releases", {}).values()]

# file_sizes = [[file.get("size", 0) for file in release] for release in releases]
# release_sizes = [sum(files) for files in file_sizes]

size_list = release_sizes.values()
total = sum(size_list)
max_release_size = max(size_list)
num_releases_remaininig = math.floor((ACCT_LIMIT - total) / max_release_size)
if num_releases_remaininig < SAFETY_CUSHION:
    from inspect import cleandoc

    msg = cleandoc(
        f"""
                    There is only space left for about {num_releases_remaininig} more releases. Free up space before trying to release more.
                    (BUT DON'T DELETE 0.11.15 w/o checking with Robert)
                    Account Max: {round(ACCT_LIMIT / GB, 2)} GB
                    Used: {round(total / GB, 2)} GB
                    Max Release Size: {round(max_release_size / MB, 1)} MB
                    """
    )
    print(msg, file=sys.stderr)
    exit(1)
