import logging
from cryptography.fernet import Fernet
import sys
import os
import logging
import json
from datetime import datetime
import dateutil.parser

from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


pl_key = "eZkaBCdeBg87CQyy6MI6WR0hpgL7-jT30tjM7T-nRZA=".encode("ascii")
fernet = Fernet(pl_key)


def decrypt(ciphertext):
    return fernet.decrypt(ciphertext)


def get_name(override=""):
    license_name = os.environ.get("LICENSE_NAME", override) or ""
    logger.debug(f"LICENSE_NAME: {license_name}")
    return license_name


def get_value(override=""):
    license_value = os.environ.get("LICENSE_VALUE", override) or ""
    logger.debug(f"LICENSE_VALUE: {license_value}")
    return license_value.encode("ascii")


class LicenseV2:
    def __init__(self, name=None, value=None):
        self.hash = LicenseV2._get_hash(get_name(name), get_value(value))

    def _get_hash(license_name, license_value):
        try:
            clear = decrypt(license_value).decode("ascii")
            parts = clear.split("|")
            if len(parts) < 2 or not parts[0] == license_name:
                logger.warning("License doesn't check out.")
                return {}
            json_str = parts[1]
            logger.info(f"License checks out: {json_str}")
            return json.loads(json_str, encoding="ascii")
        except:
            return {}

    def gpu_limit(self):
        logger.debug(f"capabilities: {self.hash}")
        return self.hash.get("gpu_limit", 0)

    def core_limit(self):
        return self.hash.get("core_limit", 1)

    def expiry(self):
        as_str = self.hash.get("expiry", datetime.utcnow().isoformat())
        return dateutil.parser.isoparse(as_str)

    def is_expired(self):
        return datetime.utcnow() < self.expiry()
