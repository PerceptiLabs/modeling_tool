import env from "@/config/env";

import { HttpRequest } from "./http";
import { KEYCLOAK_URL_CONFIG_PATH } from "../../config/constants";

export class KeyCloakRequest extends HttpRequest {
  constructor() {
    super(KEYCLOAK_URL_CONFIG_PATH, env.KEYCLOAK_BASE_URL, "sometoken");
  }

  async updateUserProfileAttributes({ payload }: { payload: unknown }) {
    await this.post(`/auth/realms/${env.KEYCLOAK_REALM}/account/`, payload);
  }
}
