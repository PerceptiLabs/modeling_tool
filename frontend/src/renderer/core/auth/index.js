import Auth0Service from "./auth0";
import KeycloakService from "./keycloak";
import NoAuthService from "./noAuth";

const AuthService = {
  _authService:
    process.env.AUTH_METHOD === "Auth0"
      ? new Auth0Service()
      : process.env.AUTH_METHOD === "Keycloak"
      ? new KeycloakService()
      : new NoAuthService(),

  init: () => {
    AuthService._authService.init();
  },
};

export default AuthService;
