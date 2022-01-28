import axios from 'axios';
import store from '@/store';

import { KEYCLOAK_URL_CONFIG_PATH, KEYCLOAK_REALM_CONFIG_PATH, KEYCLOAK_CLIENTID_CONFIG_PATH } from "@/core/constants";
import { whenUrlIsResolved } from '@/core/urlResolver';
import { isNoKeyCloakEnabled } from "./helpers";

const whenKeyCloakReady = () =>
  isNoKeyCloakEnabled()
    ? Promise.reject()
    : whenUrlIsResolved(
        KEYCLOAK_URL_CONFIG_PATH,
        process.env.KEYCLOAK_BASE_URL,
      ).then(url => {
        let ret = axios.create();
        ret.defaults.baseURL = url;
        ret.defaults.headers.common["Content-Type"] = `application/json`;
        ret.defaults.headers.common["Authorization"] = `Bearer ${store.getters["mod_user/GET_userToken"]}`;
        ret.defaults.params = {};
        return ret;
      });

export const keyCloak = {
  async url() {
    return await whenUrlIsResolved(KEYCLOAK_URL_CONFIG_PATH, process.env.KEYCLOAK_BASE_URL)
  },
  async realm() {
    return await whenUrlIsResolved(KEYCLOAK_REALM_CONFIG_PATH, process.env.KEYCLOAK_REALM)
  },
  async realm_path() {
    let r = await keyCloak.realm();
    return `/realms/${r}`;
  },
  async clientid() {
    return await whenUrlIsResolved(KEYCLOAK_CLIENTID_CONFIG_PATH, process.env.KEYCLOAK_CLIENT_ID)
  },
  updateUserProfileAttributes({ payload }) {
    return whenKeyCloakReady()
      .then(requestor => {
        return requestor.post(`${realm_path()}/account/`, payload)
      })
      .catch(console.log);
  },
  async isReachable() {
    let kc = await whenKeyCloakReady();
    let rp = await keyCloak.realm_path();
    let response = await kc.get(rp)
    return response.status == 200;
  },
};
