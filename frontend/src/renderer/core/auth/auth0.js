import { Auth0Client } from "@auth0/auth0-spa-js";

export default function Auth0Service() {
  this._instance = null;
  this._token = null;

  this.init = () => {
    this._instance = new Auth0Client({
      domain: process.env.AUTH0_CUSTOM_DOMAIN,
      client_id: process.env.AUTH0_CLIENT_ID,
      redirect_uri: window.location.origin,
      audience: process.env.AUTH0_AUDIENCE,
      useRefreshTokens: true,
    });
  };

  this.isReachable = async () => {
    return !!this._instance;
  };

  this.login = async () => {
    try {
      const { appState } = await this._instance.handleRedirectCallback();
      this._token = await this._instance.getTokenSilently();
      return appState;
    } catch (err) {
      if (err && err.error) {
        await this._instance.logout();
      } else {
        await this._instance.loginWithRedirect();
      }
    }
  };

  (this.getProfile = () => this._instance.getUser()),
    (this.userSerializer = userInfo => {
      return {
        email: userInfo.email,
        name: userInfo.name,
        nickname: userInfo.nickname,
        picture: userInfo.picture,
        sub: userInfo.sub,
        updated_at: userInfo.updated_at,
      };
    });

  this.logout = () =>
    this._instance.logout({
      returnTo: window.origin,
    });
}
