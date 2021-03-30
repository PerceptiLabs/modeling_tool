import { IUserProfile } from "@/types";
import logger from "@/core/logger";

export * from "./cookie";
export * from "./response";
export * from "./route";
export * from "./vue-utils";

export const parseJWT = (
  token: string,
  replace?: boolean,
): IUserProfile | null => {
  try {
    const base64Url = token.split(".")[1];
    let base64 = "";

    if (replace) {
      base64 = base64Url.replace("-", "+").replace("_", "/");
    } else {
      base64 = base64Url;
    }

    const userProfile = JSON.parse(window.atob(base64));

    return userProfile;
  } catch (err) {
    logger.error("parseJWT", err);
    return null;
  }
};
