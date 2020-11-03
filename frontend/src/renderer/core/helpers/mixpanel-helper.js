import { RYGG_BASE_URL } from '@/core/constants'
import { RYGG_URL_CONFIG_PATH }   from "@/core/constants";
import { RYGG_MIXPANEL_ENDPOINT }   from "@/core/constants";

import { whenUrlIsResolved } from '@/core/urlResolver';

export const resolveProxyUrl = () => {
  return whenUrlIsResolved(RYGG_URL_CONFIG_PATH, RYGG_BASE_URL)
    .then(url => {
      if (!url) { return; }

      let proxyUrl = url + RYGG_MIXPANEL_ENDPOINT;

      return proxyUrl;
    });
}

export default {
  resolveProxyUrl
}