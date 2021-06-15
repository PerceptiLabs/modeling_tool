import axios            from 'axios'
// import { objectToQueryParams } from '@/core/helpers'
// import { stringifyNetworkObjects }   from "@/core/helpers.js";

import { RYGG_BASE_URL } from '@/core/constants'
import { RYGG_URL_CONFIG_PATH }   from "@/core/constants";
import { RYGG_VERSION_CONFIG_PATH } from "@/core/constants";
import { whenUrlIsResolved } from '@/core/urlResolver';
import { whenVersionIsResolved } from '@/core/versionResolver';

const whenRyggReady = Promise.all([whenUrlIsResolved(RYGG_URL_CONFIG_PATH, RYGG_BASE_URL), whenVersionIsResolved(RYGG_VERSION_CONFIG_PATH)])
  .then(([url]) =>{
    let ret = axios.create();
    ret.defaults.baseURL = url
    ret.defaults.headers.common["Content-Type"] = `application/json`;
    ret.defaults.params = {}
    return ret
  });

export const rygg = {

  get(path) {
    return whenRyggReady.then(requestor => requestor.get(path))
  },

  delete(path) {
    return whenRyggReady.then(requestor => requestor.delete(path))
  },

  post(path, payload) {
    return whenRyggReady.then(requestor => requestor.post(path, payload))
  },

  patch(path, payload) {
    return whenRyggReady.then(requestor => requestor.patch(path, payload))
  },

  put(path, payload) {
    return whenRyggReady.then(requestor => requestor.put(path, payload))
  },
};

