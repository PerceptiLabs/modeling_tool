import { HttpRequest } from "./http";
import {
  FILESERVER_URL_CONFIG_PATH,
  FILESERVER_BASE_URL,
} from "../../config/constants";
import logger from "../logger";
import { getCookie } from "../utility";
import env from "@/config/env";

export class FileServerRequest extends HttpRequest {
  constructor() {
    super(FILESERVER_URL_CONFIG_PATH, FILESERVER_BASE_URL);

    const token =
      getCookie("fileserver_token") ||
      env.PL_FILE_SERVING_TOKEN ||
      (sessionStorage["fileserver_token"] as string);

    if (token) {
      this.setConfig("token", token);
      // Since we lose the cookie easily, save the token to session storage
      sessionStorage["fileserver_token"] = token;
    }
  }

  async isURLReachable(path: string): Promise<boolean> {
    try {
      const res = await this.get<{ response_code: number }>(
        `/is_url_reachable?path=${path}`,
      );
      return res.response_code === 200;
    } catch (err) {
      logger.error(`isURLReachable: ${path}`, err);
      return false;
    }
  }
}
