from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from requests import get
from rygg.mixpanel_proxy.apps import external_ip
from rygg.mixpanel_proxy.utils import parse_b64_to_dict
from rygg.mixpanel_proxy.utils import url_encode_mixpanel_style_params
from rygg.mixpanel_proxy.utils import parse_queryDict_to_dict

import json
from urllib.parse import parse_qs

import logging
logger = logging.getLogger(__name__)

MIXPANEL_API_JS_ENDPOINT = 'http://api-js.mixpanel.com'

MIXPANEL_TRACK_PATH = '/track/'
MIXPANEL_DECIDE_PATH = '/decide/'
MIXPANEL_ENGAGE_PATH = '/engage/'

@api_view(['GET'])
def track(request):
    # Used to event tracking

    data = request.GET.get('data', '')
    dataDict = parse_b64_to_dict(data) # data comes directly from MP

    # Setting external ip here because the user could be using NAT
    dataDict['properties']['ip'] = external_ip

    params = url_encode_mixpanel_style_params(dataDict)

    try:
        mp_response = get(url=MIXPANEL_API_JS_ENDPOINT + MIXPANEL_TRACK_PATH, params=params)
    except:
        logger.error('Error when sending tracking data to MixPanel')

    return HttpResponse()

@api_view(['POST'])
def track(request):
    # Used to event tracking

    decodedBody = parse_qs(request.body.decode('ASCII'))

    dataDict = parse_b64_to_dict(decodedBody['data'][0])

    # Setting external ip here because the user could be using NAT
    dataDict['properties']['ip'] = external_ip

    params = url_encode_mixpanel_style_params(dataDict)

    try:
        mp_response = get(url=MIXPANEL_API_JS_ENDPOINT + MIXPANEL_TRACK_PATH, params=params)
    except:
        logger.error('Error when sending tracking data to MixPanel')

    return HttpResponse()


@api_view(['GET'])
def decide(request):

    dataDict = parse_queryDict_to_dict(request.GET)
    dataDict['ip'] = external_ip

    try:
        mp_response = get(url=MIXPANEL_API_JS_ENDPOINT + MIXPANEL_DECIDE_PATH, params=dataDict)
    except:
        logger.error('Error when sending tracking data to MixPanel')

    return HttpResponse()

@api_view(['GET', 'POST'])
def engage(request):
    # Used to profile updates

    data = request.GET.get('data', '')
    dataDict = parse_b64_to_dict(data) # data comes directly from MP

    # Setting external ip here because the user could be using NAT
    dataDict['$ip'] = external_ip

    params = url_encode_mixpanel_style_params(dataDict)

    try:
        mp_response = get(url=MIXPANEL_API_JS_ENDPOINT + MIXPANEL_ENGAGE_PATH, params=params)
    except:
        logger.error('Error when updating user profile in MixPanel')

    return HttpResponse()
