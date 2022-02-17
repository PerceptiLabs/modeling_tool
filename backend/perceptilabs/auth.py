from werkzeug.wrappers import Request, Response
import cachetools.func
import json
import jwt
import re
import urllib.request

from perceptilabs.settings import AUTH_ISSUER
if AUTH_ISSUER:
    from perceptilabs.settings import AUTH_CERTS_URL, AUTH_AUDIENCE

BEARER_PATTERN = re.compile('^bearer ', re.IGNORECASE)

class AuthError(Exception):
    pass

@cachetools.func.ttl_cache(maxsize=1, ttl=10 * 60)
def get_certs_from_issuer():
    import ssl

    # TODO: Fix verification of the cert
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    return urllib.request.urlopen(AUTH_CERTS_URL, context=ctx).read()

def get_keys_from_issuer():
    if not AUTH_ISSUER:
        return None

    def decode_key(jwk):
        as_json = json.dumps(jwk)
        return jwt.algorithms.RSAAlgorithm.from_jwk(as_json)

    jwks_as_json = get_certs_from_issuer()
    jwks = json.loads(jwks_as_json)

    return {jwk['kid'] : decode_key(jwk) for jwk in jwks['keys']}


def get_issuer_key(id):
    keys = get_keys_from_issuer()
    key = keys.get(id)
    if key is None:
        raise AuthError('Public key not found.')
    return key


def jwt_decode_token(token):
    if not AUTH_ISSUER:
        return None

    try:
        header = jwt.get_unverified_header(token)
        received_key_id = header['kid']
        key = get_issuer_key(received_key_id)
        if key is None:
            raise Exception('Public key not found.')

        # audience = API identifier in auth0
        ret = jwt.decode(token, key, audience=AUTH_AUDIENCE, issuer=AUTH_ISSUER, algorithms=['RS256'])
        return ret
    except jwt.exceptions.InvalidSignatureError:
        raise AuthError('Bearer token malformed.')

def get_auth_token(req):
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        raise AuthError('Bearer token missing.')

    try:
        return re.sub(BEARER_PATTERN, '', auth_header)
    except IndexError:
        raise AuthError('Bearer token malformed.')


class jwt_middleware():

    def __init__(self, app, skipped_paths=set()):
        self.app = app
        self._skipped_paths = skipped_paths

    def __call__(self, environ, start_response):
        try:
            request = Request(environ)
            if AUTH_ISSUER and request.path not in self._skipped_paths:
                auth_token = get_auth_token(request)
                decoded = jwt_decode_token(auth_token)
                environ['user'] = decoded['sub']
                environ['auth_token'] = decoded
                environ['auth_token_raw'] = auth_token
            return self.app(environ, start_response)
        except AuthError as e:
            res = Response(f"Authorization failed: {e}", mimetype= 'text/plain', status=401)
            return res(environ, start_response)
