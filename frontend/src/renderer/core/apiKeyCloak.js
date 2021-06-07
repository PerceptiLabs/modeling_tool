import axios            from 'axios';
import store            from '@/store';

import { KEYCLOAK_URL_CONFIG_PATH, KEYCLOAK_REALM_PATH }   from "@/core/constants";
import { whenUrlIsResolved } from '@/core/urlResolver';

const whenKeyCloakReady = () =>
  whenUrlIsResolved(KEYCLOAK_URL_CONFIG_PATH, process.env.KEYCLOAK_BASE_URL)
    .then(url => {
      let ret = axios.create();
      ret.defaults.baseURL = url
      ret.defaults.headers.common["Content-Type"] = `application/json`;
      ret.defaults.headers.common['Authorization'] = `Bearer ${store.getters['mod_user/GET_userToken']}`;
      ret.defaults.params = {}
      return ret
    });

export const keyCloak = {
  url(){
    return whenUrlIsResolved(KEYCLOAK_URL_CONFIG_PATH, process.env.KEYCLOAK_BASE_URL)
  },
  updateUserProfileAttributes({ payload }) {
    return whenKeyCloakReady()
      .then(requestor => {
        return requestor.post(`${KEYCLOAK_REALM_PATH}/account/`, payload)
      });
  },
  isReachable() {
    return whenKeyCloakReady()
      .then(requestor => {
        return requestor.get(KEYCLOAK_REALM_PATH)
      })
      .then((response) => response.status == 200);
  },
};
