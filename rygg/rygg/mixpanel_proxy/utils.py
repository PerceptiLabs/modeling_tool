import base64
import json
import urllib


def parse_b64_to_dict(b64string):
    if not b64string:
        return {}

    return json.loads(base64.b64decode(b64string))

def url_encode_mixpanel_style_params(inputDict):
    if not inputDict:
        return ''

    return urllib.parse.urlencode({'data': json.dumps(inputDict)}, quote_via=urllib.parse.quote)

def parse_queryDict_to_dict(queryDict):
    if not queryDict:
        return {}

    return queryDict.dict()
