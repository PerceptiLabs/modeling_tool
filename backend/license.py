from cryptography.fernet import Fernet
import sys
import os


def _check(pl_key, access_key, secret_key):
    try:
        bin_pl_key = pl_key.encode("ascii")
        fernet = Fernet(bin_pl_key)
        bin_secret_key = secret_key.encode("ascii")
        clear = fernet.decrypt(bin_secret_key)
        bin_access_key = access_key.encode("ascii")
        return clear == bin_access_key
    except:
        return False


pl_key = "eZkaBCdeBg87CQyy6MI6WR0hpgL7-jT30tjM7T-nRZA="


# TODO : use the output of this function to determine whether they have a license.
def is_licensed():
    access_key = os.environ.get("ACCESSKEY", "")
    secret_key = os.environ.get("SECRETKEY", "")

    return _check(pl_key, access_key, secret_key)
