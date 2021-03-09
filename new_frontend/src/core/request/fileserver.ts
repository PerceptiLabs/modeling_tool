import { HttpRequest } from "./http";
import { FILESERVER_URL_CONFIG_PATH, FILESERVER_BASE_URL } from "../constants";

export class FileServerRequest extends HttpRequest {
  constructor() {
    super(FILESERVER_URL_CONFIG_PATH, FILESERVER_BASE_URL);
  }
}
