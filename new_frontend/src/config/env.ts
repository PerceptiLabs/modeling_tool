export default {
  NODE_ENV: (process.env["NODE_ENV"] as string) || "",
  BASE_URL: (process.env["BASE_URL"] as string) || "",
  HUBSPOT_ID: (process.env["VUE_APP_HUBSPOT_ID"] as string) || "",
  GOOGLE_ANALYTICS_ID:
    (process.env["VUE_APP_GOOGLE_ANALYTICS_ID"] as string) || "",
  FORCE_DEFAULT_PROJECT:
    (process.env["VUE_APP_FORCE_DEFAULT_PROJECT"] as string) || "",
  KEYCLOACK_BASE_URL:
    (process.env["VUE_APP_KEYCLOACK_BASE_URL"] as string) || "",
  KEYCLOACK_RELM: (process.env["VUE_APP_KEYCLOACK_RELM"] as string) || "",
  KEYCLOACK_CLIENT_ID:
    (process.env["VUE_APP_KEYCLOACK_CLIENT_ID"] as string) || "",
  GITHUB_CLIENT_ID: (process.env["VUE_APP_GITHUB_CLIENT_ID"] as string) || "",
  PL_FILE_SERVING_TOKEN:
    (process.env["VUE_APP_PL_FILE_SERVING_TOKEN"] as string) || "",
  ENABLE_TF2X: (process.env["VUE_APP_ENABLE_TF2X"] as boolean) || false,
  ENABLE_DATA_WIZARD:
    (process.env["VUE_APP_ENABLE_DATA_WIZARD"] as boolean) || false,
  NO_KC: (process.env["VUE_APP_NO_KC"] as boolean) || false,
};
