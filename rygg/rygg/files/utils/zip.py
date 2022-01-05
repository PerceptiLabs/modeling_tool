from more_itertools import nth, consume
from tempfile import TemporaryDirectory
from threading import Event
from typing import Iterable, Optional
from zipfile import ZipFile
import os
import re
import shutil
import sys

from rygg.files.utils.subprocesses import run_and_terminate, CanceledError
from rygg.utils.threading import async_map
from rygg.utils.collections import PresizedIterator
from rygg.settings import UNZIP_TO_TMP

import logging
logger = logging.getLogger(__name__)

def _default_dest(zipfile) -> str:
    return os.path.join(os.path.dirname(zipfile), os.path.splitext(zipfile)[0])


def _unzipped_files_from_zipfile(zipfile_name: str, dest: Optional[str]=None, cancel_token=Event()) -> PresizedIterator[str]:
    with ZipFile(zipfile_name, 'r') as zip:
        files = zip.namelist()

    if not dest:
        dest = _default_dest(zipfile_name)

    def extracted_files_list():
        with ZipFile(zipfile_name, 'r') as zip:
            for file in files:
                if cancel_token and cancel_token.is_set():
                    raise CanceledError()

                yield zip.extract(file, dest)

    return PresizedIterator(
        len(files),
        extracted_files_list())


def _get_expected_from_unzip(zipfile: str, cancel_token=Event()) -> int:
    lines = run_and_terminate(cancel_token, ["unzip", "-Z", "-h", zipfile])
    second_line = nth(lines, 1, default="")
    pattern = r'Zip file size: .* bytes, number of entries: (?P<count>\d*)'
    m = re.match(pattern, second_line)
    return int(m.group("count"))

def _get_items_from_unzip(zipfile: str, dest: Optional[str]=None, cancel_token=Event()) -> Iterable[str]:
    # Specific to unzip version 6.00
    IS_CONTENT = lambda line: not line.startswith("-")
    HEADER_LINE_COUNT=1

    if not dest:
        dest = _default_dest(zipfile)

    lines = run_and_terminate(cancel_token, ["unzip", "-o", zipfile, "-d", dest])

    # skip header
    consume(lines, HEADER_LINE_COUNT)
    for line in lines:
        pathparts = line.split(":", 2)[1:2]
        if pathparts:
            yield pathparts[0].strip()

def _unzipped_files_from_unzip(zipfile: str, dest: Optional[str]=None, cancel_token=Event()) -> Iterable[str]:
    return PresizedIterator(
        _get_expected_from_unzip(zipfile, cancel_token=cancel_token),
        _get_items_from_unzip(zipfile, dest=dest, cancel_token=cancel_token))


def _copied_files_from_unzip(zipfile, dest: Optional[str]=None, cancel_token=Event()) -> PresizedIterator[str]:
    if not dest:
        dest = _default_dest(zipfile)


    def inner():
        with TemporaryDirectory() as tmp:
            def copy_to_dest(f: str) -> str:
                rel = os.path.relpath(f, tmp)
                destfile = os.path.join(dest, rel)
                if os.path.isfile(f):
                    destdir = os.path.dirname(destfile)
                    os.makedirs(destdir, exist_ok=True)
                    shutil.copyfile(f, destfile)
                elif os.path.isdir(f):
                    os.makedirs(destfile, exist_ok=True)
                return destfile

            unzipped = _get_items_from_unzip(zipfile, dest=tmp, cancel_token=cancel_token)

            for copied in async_map(unzipped, copy_to_dest, cancel_token):
                yield copied

    return PresizedIterator(
        _get_expected_from_unzip(zipfile, cancel_token=cancel_token),
        inner())

def _get_unzipper():
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
        if UNZIP_TO_TMP:
            logger.debug("Unzipping to temp dir")
            return _copied_files_from_unzip
        else:
            logger.debug("Unzipping to destination dir")
            return _unzipped_files_from_unzip
    else:
        logger.debug("Unzipping to destination dir with zipfile library")
        return _unzipped_files_from_zipfile


def unzipped_files(zipfile: str, dest: Optional[str]=None, cancel_token=Event()) -> PresizedIterator[str]:
    if not os.path.isfile(zipfile):
        raise FileNotFoundError(zipfile)

    if dest and os.path.exists(dest) and not os.path.isdir(dest):
        raise Exception(f"Destination {dest} exists but isn't a directory")

    unzipper = _get_unzipper()
    return unzipper(zipfile, dest=dest, cancel_token=cancel_token)

