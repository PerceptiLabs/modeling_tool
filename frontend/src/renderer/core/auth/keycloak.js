export default function KeycloakService() {
  this.init = () => {
    console.log("Keycloak Service Init");
  }
  this.isReachable = async () => {
    return false;
  };
}
