import { RyggRequest } from "./rygg";
import { KeyCloakRequest } from "./keyCloak";
import { SocketRequest } from "./socket";
import { FileServerRequest } from "./fileserver";

export default {
  rygg: new RyggRequest(),
  keyCloak: new KeyCloakRequest(),
  fileServer: new FileServerRequest(),

  core: new SocketRequest(),
};
