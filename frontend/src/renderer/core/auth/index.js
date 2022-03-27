import Auth0Service from "./auth0";
import KeycloakService from "./keycloak";
import NoAuthService from "./noAuth";

const AuthService = {
  _authInstance:
    process.env.AUTH_METHOD === "Auth0"
      ? new Auth0Service()
      : process.env.AUTH_METHOD === "Keycloak"
      ? new KeycloakService()
      : new NoAuthService(),

  init: () => AuthService._authInstance.init(),
  isReachable: () => AuthService._authInstance.isReachable(),
  login: () => AuthService._authInstance.login(),
  logout: () => AuthService._authInstance.logout(),
  getToken: () => AuthService._authInstance._token,
};

export default AuthService;
