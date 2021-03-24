import { RyggRequest } from "./rygg";
import { KeyCloakRequest } from "./keyCloak";
import { SocketRequest } from "./socket";
import { FileServerRequest } from "./fileserver";

export const rygg = new RyggRequest();
export const keyCloak = new KeyCloakRequest();
export const fileServer = new FileServerRequest();
export const core = new SocketRequest();

export default {
  rygg,
  keyCloak,
  fileServer,
  core,
};
