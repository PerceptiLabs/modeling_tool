from cryptography.fernet import Fernet
import sys
import os
import logging

log = logging.getLogger(__name__)


def _check(pl_key, license_name, license_value):
    try:
        bin_pl_key = pl_key.encode("ascii")
        fernet = Fernet(bin_pl_key)
        bin_value = license_value.encode("ascii")
        clear = fernet.decrypt(bin_value)
        bin_name = license_name.encode("ascii")
        return clear == bin_name
    except:
        return False


pl_key = "eZkaBCdeBg87CQyy6MI6WR0hpgL7-jT30tjM7T-nRZA="


def is_licensed():
    license_name = os.environ.get("LICENSE_NAME", "")
    log.debug(f"LICENSE_NAME: {license_name}")
    license_value = os.environ.get("LICENSE_VALUE", "")
    log.debug(f"LICENSE_VALUE: {license_value}")

    ret = _check(pl_key, license_name, license_value)
    if ret:
        log.info(f"License checks out.")
    else:
        log.warning(f"License doesn't check out.")

    return ret
