import { HttpRequest } from "./http";
import { RYGG_BASE_URL, RYGG_URL_CONFIG_PATH } from "../../config/constants";

export class RyggRequest extends HttpRequest {
  constructor() {
    super(RYGG_URL_CONFIG_PATH, RYGG_BASE_URL);
  }
}
