import base64
import json
import urllib


def parse_b64_to_dict(b64string):
    if not b64string:
        return {}

    try:
        return json.loads(base64.b64decode(b64string))
    except:
        raise HTTPExceptions.BAD_REQUEST.with_content(f"Error parsing b64 string: {str(b64string)}")

def url_encode_mixpanel_style_params(inputDict):
    if not inputDict:
        return ''

    try:
        return urllib.parse.urlencode({'data': json.dumps(inputDict)}, quote_via=urllib.parse.quote)
    except:
        raise HTTPExceptions.BAD_REQUEST.with_content(f"Error encoding JSON: {str(inputDict)}")


def parse_queryDict_to_dict(queryDict):
    if not queryDict:
        return {}

    try:
        return queryDict.dict()
    except:
        raise HTTPExceptions.BAD_REQUEST.with_content(f"Error converting QueryDict to Dict: {str(inputDict)}")
