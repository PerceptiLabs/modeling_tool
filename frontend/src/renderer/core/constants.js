const isDevelopMode = process.env.NODE_ENV !== 'production';

const trainingElements  = ['TrainNormal', 'TrainRegression', 'TrainReinforce', 'TrainGan', 'TrainDetector'
  //'TrainGenetic',
  //'TrainDynamic',
  //'TrainLoss',
  //'TrainOptimizer',
];
const deepLearnElements = [
  'DeepLearningFC',
  'DeepLearningConv',
  'DeepLearningRecurrent',
  'PreTrainedVGG16',
  'PreTrainedResNet50',
  'PreTrainedInceptionV3',
  'PreTrainedMobileNetV2',
  'UNet',
];


const pathWebWorkers = './static/webworkers';

const baseUrlCloud  = 'https://perceptilabsamerica.azurewebsites.net/api/';
const baseUrlSite   = 'https://perceptilabs.com';

const baseHost = window.location.hostname

export const KEYCLOAK_URL_CONFIG_PATH = 'keycloak_url';
export const IS_ENTERPRISE_CONFIG_PATH = 'is_enterprise';

export const RYGG_URL_CONFIG_PATH = 'rygg_url';
export const RYGG_VERSION_CONFIG_PATH = 'rygg_version';
export const RYGG_BASE_URL = `http://${baseHost}:8000`
export const RYGG_MIXPANEL_ENDPOINT = '/mixpanel'; // MixPanel proxy functions

export const KERNEL_URL_CONFIG_PATH = 'kernel_url';
export const KERNEL_VERSION_CONFIG_PATH = 'kernel_version';
export const KERNEL_BASE_URL = `ws://${baseHost}:5000`
// for legacy stuff in apiCore
export const KERNEL_HOST = baseHost
export const KERNEL_PORT = 5000

export const RENDERING_KERNEL_URL_CONFIG_PATH = 'rendering_kernel_url';
export const RENDERING_KERNEL_BASE_URL = `http://${baseHost}:5001`

export const GITHUB_AUTHORIZE_URL = `https://github.com/login/oauth/authorize?scope=public_repo,read:user&client_id=${process.env.GITHUB_CLIENT_ID}`;
export const GITHUB_GET_TOKEN_BY_CODE_URL = 'https://ghsk.azurewebsites.net'

export const KEYCLOAK_REALM_PATH = `/realms/${process.env.KEYCLOAK_REALM}`;

export const PERCEPTILABS_DOCUMENTATION_URL = 'https://docs.perceptilabs.com/perceptilabs';
export const PERCEPTILABS_YOUTUBE_VIDEO_TUTORIAL_URL = 'https://www.youtube.com/watch?v=IDC_uHfdpnw&list=PLhDSeRDt1gigF-8DrTBedYy3TMZ2OelqA';
export const PERCEPTILABS_VIDEO_TUTORIAL_URL = 'https://docs.perceptilabs.com/perceptilabs/getting-started/video-tutorials';
export const PERCEPTILABS_YOUTUBE_URL = 'https://www.youtube.com/channel/UCYAWJ3u8N6E6OI7GjIUe-Iw';
export const PERCEPTILABS_SLACK_URL = 'https://join.slack.com/t/perceptilabs-com/shared_invite/zt-mxohtpkm-lQI_0nT~tBeUd2RtZIfe4g'
export const PERCEPTILABS_FORUM_URL = 'https://forum.perceptilabs.com/';
export const PERCEPTILABS_BLOGS_URL = 'https://blog.perceptilabs.com/';

export const USER_FLOW_CONTENT_ID ='31837726-6d95-47ba-9361-6a6cd15012a8';

const widthElement = 60;
const workspaceGrid = 30;
export const SHIFT_HOLDING_CONNECT_COMPONENT_MAX_DISTANCE = 250;

export const workspaceGridSmallGapSize = 30;
export const workspaceGridBigGapSize = 150;
export const shadowBoxDragIfMoreThenElementsSelected = 3;
const pathSlash = process.platform === 'win32' ? '\\' : '/';

const hideSidebarOnBreakpoint = 1280;
const sidebarNavCoefficientScaleCalculateFromHeight = 920;
const filePickerStorageKey = 'filePickerPathSource';
const localStorageGridKey = 'isGridEnabled';

export const localStorageThemeKey = 'theme';
export const THEME_LIGHT = 'light';
export const THEME_DARK = 'dark';

export const sessionStorageInstanceIdKey = 'perceptilabs_instance_id';

export const MODAL_PAGE_PROJECT = 'MODAL_PAGE_PROJECT';
export const MODAL_PAGE_WHATS_NEW = 'MODAL_PAGE_WHATS_NEW';
export const MODAL_PAGE_CREATE_MODEL = 'MODAL_PAGE_CREATE_MODEL';
export const MODAL_PAGE_QUESTIONNAIRE = 'MODAL_PAGE_QUESTIONNAIRE';

export const PROJECT_DEFAULT_FOLDER = '/Users/antonbourosu/proj/'


export const TRACKER_SCREENNAME_PROJECTS = 'Projects';
export const TRACKER_SCREENNAME_PROJECTS_TRAINING = 'Projects-Training';
export const TRACKER_SCREENNAME_WORKSPACE = 'Workspace';
export const TRACKER_SCREENNAME_WORKSPACE_TRAINING = 'Workspace-Training';
export const TRACKER_SCREENNAME_STATISTICS = 'Statistics';
export const TRACKER_SCREENNAME_STATISTICS_TRAINING = 'Statistics-Training';
export const TRACKER_SCREENNAME_TEST = 'Test';
export const TRACKER_SCREENNAME_TEST_TRAINING = 'Test-Training';

export const LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY  = 'mod_workspace_view_type'
export const LOCAL_STORAGE_WORKSPACE_SHOW_MODEL_PREVIEWS  = 'show_model_previews'
export const LOCAL_STORAGE_HIDE_DELETE_MODAL = 'hide_delete_modal'

// export const ENTERPRISE_DATASET_FOLDER_PREFIX = '/Users/dred/PL_FILES/';
export const ENTERPRISE_DATASET_FOLDER_PREFIX = '/perceptilabs/Documents/Perceptilabs/data/';

export const defaultTrainingSettings = {
  Epochs: 100,
  Batch_size: 32,
  Shuffle: true,
  Loss: 'Quadratic', //[Cross-Entropy, Quadratic, Weighted Cross-Entropy, Dice]
  LossOptions: [
    {text: 'Cross-Entropy', value: 'Cross-Entropy'},
    {text: 'Quadratic', value: 'Quadratic'},
    {text: 'Dice', value: 'Dice'},
  ],
  Learning_rate: 0.001,
  Optimizer: 'ADAM', // [ADAM,SGD,Adagrad,RMSprop]
  OptimizerOptions: [
    {text: 'ADAM', value: 'ADAM'},
    {text: 'SGD', value: 'SGD'},
    {text: 'Adagrad', value: 'Adagrad'},
    {text: 'RMSprop', value: 'RMSprop'},
  ],
  Beta1: 0.9,
  Beta2: 0.999,
  Momentum: 0,
  Centered: false,
  AutoCheckpoint: false,
}

// those components can't be delete | copy | cut | paste
export const lockedComponentsNames = [
  'IoInput',
  'IoOutput',
]

export {
  isDevelopMode,
  trainingElements,
  deepLearnElements,
  pathWebWorkers,
  widthElement,
  workspaceGrid,
  baseUrlCloud,
  baseUrlSite,
  pathSlash,
  hideSidebarOnBreakpoint,
  sidebarNavCoefficientScaleCalculateFromHeight,
  filePickerStorageKey,
  localStorageGridKey,
}

export const TestTypes = {
  confusion_matrix: {
    default: false,
    disabled: false,
    text: 'Confusion Matrix'
  },
  classification_metrics: {
    default: false,
    disabled: false,
    text: 'Classification Metrics',
  },
  segmentation_metrics: {
    default: false,
    disable: false,
    text: 'Segmentation Metrics',
  },
  outputs_visualization: {
    default: false,
    disable: false,
    text: 'Output Visualization',
  },
  // forward_prop: {
  //   default: false,
  //   disabled: true,
  //   text: 'Forward Prop'
  // }
}
