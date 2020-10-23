from django.apps import AppConfig
from django.conf import settings
from requests import get

external_ip = None

class MixpanelProxyConfig(AppConfig):
    name = 'mixpanel_proxy'

    # Makes sure the MixpanelProxyConfig isn't needlessly run twice
    hasLoaded = False

    def ready(self):

        if MixpanelProxyConfig.hasLoaded: return

        global external_ip

        try:
            external_ip = get(settings.EXTERNAL_IP_RESOLVER_ENDPOINT).text
        except:
            external_ip = ''

        hasLoaded = True
