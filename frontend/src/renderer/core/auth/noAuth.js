export default function NoAuthService() {
  this.init = () => {
    console.log("NoAuth Service Init");
  }
  
  this.isReachable = async () => {
    return false;
  };
}
