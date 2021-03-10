import env from "@/config/env";

export const isDevelopMode = env.NODE_ENV !== "production";

export const trainingElements = [
  "TrainNormal",
  "TrainRegression",
  "TrainReinforce",
  "TrainGan",
  "TrainDetector",
  //'TrainGenetic',
  //'TrainDynamic',
  //'TrainLoss',
  //'TrainOptimizer',
];
export const deepLearnElements = [
  "DeepLearningFC",
  "DeepLearningConv",
  "DeepLearningRecurrent",
];

export const pathWebWorkers = "./workers";

export const baseUrlCloud =
  "https://perceptilabsamerica.azurewebsites.net/api/";
export const baseUrlSite = "https://perceptilabs.com";

const baseHost = window.location.hostname;

export const KEYCLOAK_URL_CONFIG_PATH = "keycloak_url";

export const FILESERVER_URL_CONFIG_PATH = "fileserver_url";
export const FILESERVER_BASE_URL = `http://${baseHost}:8011`;

export const RYGG_URL_CONFIG_PATH = "rygg_url";
export const RYGG_BASE_URL = `http://${baseHost}:8000`;
export const RYGG_MIXPANEL_ENDPOINT = "/mixpanel"; // MixPanel proxy functions

export const KERNEL_URL_CONFIG_PATH = "kernel_url";
export const KERNEL_BASE_URL = `ws://${baseHost}:5000`;

export const GITHUB_AUTHORIZE_URL = `https://github.com/login/oauth/authorize?scope=public_repo,read:user&client_id=${env.GITHUB_CLIENT_ID}`;
export const GITHUB_GET_TOKEN_BY_CODE_URL = "https://ghsk.azurewebsites.net";

export const IS_VALID_KEYCLOACK_CHECKER_URL = `${env.KEYCLOACK_BASE_URL}/auth/realms/${env.KEYCLOACK_RELM}/protocol/openid-connect/3p-cookies/step1.html`;

export const widthElement = 60;
export const workspaceGrid = 30;

export const workspaceGridSmallGapSize = 30;
export const workspaceGridBigGapSize = 150;
export const shadowBoxDragIfMoreThenElementsSelected = 3;
// export const pathSlash = process.platform === 'win32' ? '\\' : '/';

export const hideSidebarOnBreakpoint = 1280;
export const sidebarNavCoefficientScaleCalculateFromHeight = 920;
export const filePickerStorageKey = "filePickerPathSource";
export const localStorageGridKey = "isGridEnabled";

export const MODAL_PAGE_PROJECT = "MODAL_PAGE_PROJECT";
export const MODAL_PAGE_WHATS_NEW = "MODAL_PAGE_WHATS_NEW";
export const MODAL_PAGE_CREATE_MODEL = "MODAL_PAGE_CREATE_MODEL";
export const MODAL_PAGE_QUESTIONNAIRE = "MODAL_PAGE_QUESTIONNAIRE";

export const PROJECT_DEFAULT_FOLDER = "/Users/antonbourosu/proj/";

export const TRACKER_SCREENNAME_PROJECTS = "Projects";
export const TRACKER_SCREENNAME_PROJECTS_TRAINING = "Projects-Training";
export const TRACKER_SCREENNAME_WORKSPACE = "Workspace";
export const TRACKER_SCREENNAME_WORKSPACE_TRAINING = "Workspace-Training";
export const TRACKER_SCREENNAME_STATISTICS = "Statistics";
export const TRACKER_SCREENNAME_STATISTICS_TRAINING = "Statistics-Training";
export const TRACKER_SCREENNAME_TEST = "Test";
export const TRACKER_SCREENNAME_TEST_TRAINING = "Test-Training";

export const LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY = "mod_workspace_view_type";
export const LOCAL_STORAGE_WORKSPACE_SHOW_MODEL_PREVIEWS =
  "show_model_previews";
export const LOCAL_STORAGE_HIDE_DELETE_MODAL = "hide_delete_modal";
