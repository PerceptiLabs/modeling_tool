import axios            from 'axios';
import store            from '@/store';

import { KEYCLOAK_URL_CONFIG_PATH }   from "@/core/constants";
import { whenUrlIsResolved } from '@/core/urlResolver';

const whenKeyCloakReady = () => 
  whenUrlIsResolved(KEYCLOAK_URL_CONFIG_PATH, process.env.KEYCLOACK_BASE_URL)
    .then(url => {
      let ret = axios.create();
      ret.defaults.baseURL = url
      ret.defaults.headers.common["Content-Type"] = `application/json`;
      ret.defaults.headers.common['Authorization'] = `Bearer ${store.getters['mod_user/GET_userToken']}`;
      ret.defaults.params = {}
      return ret
    });

export const keyCloak = {
  updateUserProfileAttributes({ payload }) {
    return whenKeyCloakReady()
      .then(requestor => {
        return requestor.post(`/auth/realms/${process.env.KEYCLOACK_RELM}/account/`, payload)
      });
  },
};
