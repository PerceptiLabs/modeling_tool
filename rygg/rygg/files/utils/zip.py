from more_itertools import nth, consume
from rygg.files.utils.subprocesses import run_and_terminate, CanceledError
from zipfile import ZipFile
import os
import re

def default_dest(zipfile):
    return os.path.join(os.path.dirname(zipfile), os.path.splitext(zipfile)[0])


def unzipped_files_from_zipfile(zipfile_name, dest=None, cancel_token=None):

    # TODO: is it performant to open the zip twice?
    with ZipFile(zipfile_name, 'r') as zip:
        files = zip.namelist()

    files_count = len(files)
    if not dest:
        dest = default_dest(zipfile_name)

    if files_count > 0:
        os.makedirs(dest, exist_ok=True)

    def extracted_files_list():
        with ZipFile(zipfile_name, 'r') as zip:
            for file in files:
                if cancel_token and cancel_token.is_set():
                    raise CanceledError()

                yield zip.extract(file, dest)

    return files_count, extracted_files_list()


def unzipped_files_from_unzip(zipfile, dest=None, cancel_token=None):
    if not dest:
        dest = default_dest(zipfile)

    def get_expected():
        lines = run_and_terminate(cancel_token, ["unzip", "-Z", "-h", zipfile])
        second_line = nth(lines, 1, default="")
        pattern = r'Zip file size: .* bytes, number of entries: (?P<count>\d*)'
        m = re.match(pattern, second_line)
        return int(m.group("count"))

    def get_items():
        # Specific to unzip version 6.00
        IS_CONTENT = lambda line: not line.startswith("-")
        HEADER_LINE_COUNT=1

        lines = run_and_terminate(cancel_token, ["unzip", "-o", zipfile, "-d", dest])

        # skip header
        consume(lines, HEADER_LINE_COUNT)
        for line in lines:
            pathparts = line.split(":", 2)[1:2]
            if pathparts:
                yield pathparts[0].strip()


    return get_expected(), get_items()

def get_unzipper():
    def check_unzip_version():
        SUPPORTED_VERSION="6.00"

        lines = run_and_terminate(None, ["unzip", "-v"])
        first_line = nth(lines, 0, default="")
        ok = first_line.startswith(f"UnZip {SUPPORTED_VERSION}")
        if not ok:
            raise Exception(f"Wrong version of unzip. Expected {SUPPORTED_VERSION}. Got version string '{first_line}'")

    def has_unzip():
        try:
            check_unzip_version()
            return True
        except:
            return False

    if has_unzip():
        return unzipped_files_from_unzip
    else:
        return unzipped_files_from_zipfile

def unzipped_files(zipfile, dest=None, cancel_token=None):
    if not os.path.isfile(zipfile):
        raise FileNotFoundError(zipfile)

    if dest and os.path.exists(dest) and not os.path.isdir(dest):
        raise Exception(f"Destination {dest} exists but isn't a directory")

    unzipper = get_unzipper()
    return unzipper(zipfile, dest=dest, cancel_token=cancel_token)

