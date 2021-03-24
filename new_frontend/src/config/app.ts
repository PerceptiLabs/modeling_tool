import { App as VueApp, createApp } from "vue";
import { getModule } from "vuex-module-decorators";
import Keycloak from "keycloak-js";

import { parseJWT } from "@/utility";
import logger from "@/core/logger";
import request from "@/core/request";
import App from "@/App.vue";
import router from "@/router";
import store from "@/store";
import UserModule from "@/store/modules/mod_user";
import env from "./env";
import { isDevelopMode, IS_VALID_KEYCLOACK_CHECKER_URL } from "./constants";

// plugins
import setupPlugins from "@/plugins";
import setupDirectives from '@/directives';

class AppInstance {
  private _appInstance: VueApp<Element> | null = null;
  private _keycloak: Keycloak.KeycloakInstance | null = null;

  private readonly _initOptions = {
    url: `${env.KEYCLOACK_BASE_URL}/auth`,
    realm: `${env.KEYCLOACK_RELM}`,
    clientId: `${env.KEYCLOACK_CLIENT_ID}`,
    onLoad: "login-required" as Keycloak.KeycloakOnLoad,
    checkLoginIframe: false, // only true when onLoad is set to 'check-sso', causes errors when offline
  };

  get instance() {
    return this._appInstance;
  }

  get keycloak() {
    return this._keycloak;
  }

  async initialize() {
    try {
      const isKeycloackReachable = await request.fileServer.isURLReachable(
        IS_VALID_KEYCLOACK_CHECKER_URL,
      );

      if (env.NO_KC == true) {
        this.demo();
      } else if (isKeycloackReachable) {
        await this.login();
      } else {
        throw new Error("No Internet Connection!");
      }
    } catch (err) {
      logger.error(err);
    }
  }

  private async login() {
    this._keycloak = Keycloak(this._initOptions);

    const auth = await this._keycloak.init({
      onLoad: this._initOptions.onLoad,
      checkLoginIframe: this._initOptions.checkLoginIframe,
    });

    if (!auth) {
      window.location.reload();
    }

    this.runApp(this._keycloak.token!, this._keycloak.refreshToken!);
  }

  private demo() {
    const user = {
      firstName: "John",
      lastName: "Doe",
      email: "a@a.test",
      userId: 1,
    };

    const token = "placeholder." + window.btoa(JSON.stringify(user));
    const refreshToken = "placeholder_refreshToken";
    this.runApp(token, refreshToken);
  }

  private runApp(token: string, refreshToken: string) {
    this._appInstance = createApp(App);
    this._appInstance.use(store).use(router).mount("#app");

    this.setTokens(token, refreshToken);

    this.setRefreshTokenWorker();
    this.setAppConfig();
    setupPlugins(this._appInstance);
    setupDirectives(this._appInstance);
  }

  private setTokens(token: string, refreshToken: string) {
    const userStore = getModule(UserModule, store);

    userStore.setToken(token, refreshToken);
  }

  private async setRefreshTokenWorker() {
    // Get new token 5 mins before it's expired
    const parsedJWT = parseJWT(this._keycloak.token!);
    const remainedSeconds = Math.round(
      parsedJWT.exp - new Date().getTime() / 1000,
    );

    setTimeout(() => this.checkToken(), (remainedSeconds - 5 * 60) * 1000);
  }

  async checkToken(): Promise<boolean> {
    try {
      // Refresh token so that token can be valid for next 24 hours
      const refreshed = await this._keycloak.updateToken(
        24 * 60 * 60 /* 24 hours */,
      );
      if (refreshed) {
        this.setTokens(this._keycloak.token!, this._keycloak.refreshToken!);
      }
      return true;
    } catch (e) {
      logger.error("Authentication Failed: ", e);
      return false;
    }
  }

  private setAppConfig() {
    if (this._appInstance) {
      this._appInstance.config.performance = isDevelopMode;
    }
  }
}

const appInstance = new AppInstance();

export default appInstance;
