<template lang="pug">
#app.theme-transition(:class="`${theme}-theme`")
  app-header.app-header(v-if="showMenuBar")
  .d-flex.app-page
    sidebar-menu
    router-view.flex-1
  the-info-popup(v-if="showPopup")
  confirm-popup
  PiPyPopupUpdate(v-if="showPiPyNotification")
  create-issue-popup(v-if="showCreateIssuesPopup")
  modal-pages-engine
  about-app-popup(v-if="showAppAboutPopUp")
  add-card-popup(v-if="showAddCardPopup")
</template>
<script>
import {
  isOsMacintosh,
  isBrowserChromeOrFirefox,
} from "@/core/helpers";
import CreateIssuePopup from "@/components/global-popups/create-issues-popup.vue";
import {
  getModelJsonById as rygg_getModelJsonById,
  createDataset as rygg_createDataset,
  attachModelsToDataset as rygg_attachModelsToDataset,
} from "@/core/apiRygg";
import Analytics from "@/core/analytics";
import {
  LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY,
  localStorageGridKey,
  THEME_LIGHT,
  THEME_DARK,
} from "@/core/constants.js";
import { mapMutations, mapActions, mapGetters, mapState } from "vuex";
import { getModelDatasetPath } from "@/core/modelHelpers.js";
import { assembleModel } from "@/core/helpers/model-helper";
import SidebarMenu from "@/pages/layout/sidebar-menu.vue";
import AppHeader from "@/components/app-header/app-header.vue";
import PiPyPopupUpdate from "@/components/global-popups/update-popup/pipy-update-popup.vue";
import TheInfoPopup from "@/components/global-popups/the-info-popup.vue";
import ConfirmPopup from "@/components/global-popups/confirm-popup.vue";
import ModalPagesEngine from "@/components/modal-pages-engine.vue";
import AboutAppPopup from "@/components/global-popups/about-app-popup.vue";
import AddCardPopup from "@/components/global-popups/add-card-popup.vue";
import {
  MODAL_PAGE_PROJECT,
  MODAL_PAGE_QUESTIONNAIRE,
} from "@/core/constants.js";
import { isEnterpriseApp } from "@/core/apiRygg.js";
import { keyCloak } from "@/core/apiKeyCloak.js";

export default {
  name: "TheApp",
  components: {
    SidebarMenu,
    ModalPagesEngine,
    TheInfoPopup,
    ConfirmPopup,
    CreateIssuePopup,
    PiPyPopupUpdate,
    AboutAppPopup,
    AddCardPopup,
    AppHeader,
  },
  beforeCreate() {
    this.$store.dispatch("mod_api/API_setAppInstance");
  },
  async created() {
    if (!isBrowserChromeOrFirefox()) {
      this.$store.dispatch(
        "globalView/GP_infoPopup",
        "PerceptiLabs works best in FireFox and Chrome, we suggest you use the tool there instead for the best experience.",
      );
    }
    window.addEventListener("beforeunload", e => {
      let networksHaveChanges = this.networksWithChanges.some(id =>
        this.getWorkspacesIds.includes(id),
      );
      if (networksHaveChanges) {
        const confirmationMessage = "It looks like you have edited model.";

        (e || window.event).returnValue = confirmationMessage; //Gecko + IE

        return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
      }
    });
    window.addEventListener("online", this.updateOnlineStatus);
    window.addEventListener("offline", this.updateOnlineStatus);
    this.trackerInit();
    this.readUserInfo();
    this.checkRyggAvailability();

    this.$store.commit("mod_project/setIsDefaultProjectMode");
    await isEnterpriseApp().then(isEnterpriseAppValue => {
      return this.$store.commit(
        "globalView/set_isEnterpriseApp",
        isEnterpriseAppValue,
      );
    });
  },
  async mounted() {
    this.$intercom.boot({
      hide_default_launcher: true,
    });

    this.getPyPiUpdate();

    if (this.isDefaultProjectMode) {
      // in the free version, the user is locked to a single project
      let defaultProject = await this.getDefaultModeProject();
      let project_id = defaultProject.project_id;
      this.$store.dispatch("mod_datasets/getDatasets", {}, project_id);
      this.fetchNetworkMetas(defaultProject);
    } else if (this.isProjectSelected) {
      const currentProjectId = this.$store.state.mod_project.currentProject;

      let currentProject = await this.getProject(currentProjectId);
      if (currentProject) {
        this.fetchNetworkMetas(currentProject);
      }
    } else {
      await this.getProjects();
      if (localStorage.hasOwnProperty("currentUser")) {
        this.setActivePageAction(MODAL_PAGE_PROJECT);
      }
    }

    this.$store.dispatch("mod_datasets/getDatasets");

    if (localStorage.hasOwnProperty(localStorageGridKey)) {
      const gridValue = localStorage.getItem(localStorageGridKey) === "true";
      this.$store.commit("globalView/setGridStateMutation", gridValue);
    }

    this.$store.commit(
      "mod_workspace-changes/get_workspaceChangesInLocalStorage",
    );

    this.serViewType();

    this.$store.dispatch("mod_api/checkCoreVersions", null, { root: true });

    this.updateOnlineStatus();
    this.SET_appVersion(process.env.PACKAGE_VERSION);
    // document.body.style.overflow = 'hidden';
    document.addEventListener("keydown", this.disableHotKeys);

    // this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage');

    if (!this.user) this.cloud_userGetProfile();

  },
  beforeDestroy() {
    window.removeEventListener("online", this.updateOnlineStatus);
    window.removeEventListener("offline", this.updateOnlineStatus);
    document.removeEventListener("keydown", this.disableHotKeys);
  },
  data() {
    return {
      showMacHeader: true,
    };
  },
  computed: {
    ...mapState({
      theme: state => state.globalView.theme,
    }),
    ...mapGetters({
      user: "mod_user/GET_userProfile",
      email: "mod_user/GET_userEmail",
      isDefaultProjectMode: "mod_project/GET_isDefaultProjectMode",
      currentProject: "mod_project/GET_project",
      isProjectSelected: "mod_project/GET_isProjectSelected",
      viewType: "mod_workspace/GET_viewType",
      currentModelIndex: "mod_workspace/GET_currentModelIndex",
      currentStatsIndex: "mod_workspace/GET_currentStatsIndex",
      currentTestIndex: "mod_workspace/GET_currentTestIndex",
      networksWithChanges: "mod_workspace-changes/get_networksWithChanges",
      showPiPyNotification:
        "mod_workspace-notifications/getPiPyShowNotification",
      emptyNavigationMode: "mod_empty-navigation/getEmptyScreenMode",
      allModelsDatasets: "mod_datasets/GET_datasets",
    }),
    workspaceContent() {
      return this.$store.state["mod_workspace"].workspaceContent;
    },
    showNotAvailable() {
      return this.$store.state.mod_autoUpdate.showNotAvailable;
    },
    showNewModelPopup() {
      return this.$store.state.globalView.globalPopup.showNewModelPopup;
    },
    userId() {
      return this.$store.getters["mod_user/GET_userID"];
    },
    userProfile() {
      return this.$store.getters["mod_user/GET_userProfile"];
    },
    isUserFirstLogin() {
      return this.$store.getters["mod_user/GET_isUserFirstLogin"];
    },
    /*show popup*/
    infoPopup() {
      return this.$store.state.globalView.globalPopup.showInfoPopup;
    },
    errorPopup() {
      return this.$store.state.globalView.globalPopup.showErrorPopup;
    },
    showPopup() {
      return (
        this.errorPopup.length || (this.infoPopup && this.infoPopup.length)
      );
    },
    showMenuBar() {
      const GET_userIsLogin = this.$store.getters["mod_user/GET_userIsLogin"];
      return GET_userIsLogin;
    },
    showCreateIssuesPopup() {
      return this.$store.state.globalView.globalPopup.showCreateIssuesPopup;
    },
    currentNetworkId() {
      return this.$store.getters["mod_workspace/GET_currentNetworkId"];
    },
    unparsedModels() {
      return this.$store.state.mod_workspace.unparsedModels.map(
        m => m.model_id,
      );
    },
    showAppAboutPopUp() {
      return this.$store.state.globalView.globalPopup.showAppAbout;
    },
    showAddCardPopup() {
      return this.$store.state.globalView.globalPopup.showAddCardPopup;
    },
    getWorkspacesIds() {
      return this.$store.state[
        "mod_workspace"
      ].workspaceContent.map(workspace => workspace.networkID.toString());
    },
  },
  watch: {
    userId(newVal) {
      Analytics.googleAnalytics.trackUserId(
        this.$store.getters["mod_user/GET_userID"],
      );
    },
    userProfile(newVal) {
      if (!newVal || newVal.email === "Guest") {
        return;
      }

      setTimeout(() => {
        this.trackerCreateUser(newVal);
        this.trackerUpdateUser(newVal);
        this.trackerInitUser(newVal);
        this.initIntercom();
      }, 5000);
    },
  },
  methods: {
    ...mapMutations({
      SET_appVersion: "globalView/SET_appVersion",
      SET_appIsFullView: "globalView/SET_appIsFullView",

      // loadProjectFromLocalStorage: 'mod_workspace/get_workspacesFromLocalStorage',
      // setPageTitleMutation: 'globalView/setPageTitleMutation',

      deleteNetworkById: "mod_workspace/delete_networkById",
      setViewTypeMutation: "mod_workspace/setViewTypeMutation",
    }),
    ...mapActions({
      openErrorPopup: "globalView/GP_infoPopup",
      SET_onlineStatus: "globalView/SET_onlineStatus",

      trackerInit: "mod_tracker/TRACK_initMixPanel",
      trackerInitUser: "mod_tracker/TRACK_initMixPanelUser",
      trackerCreateUser: "mod_tracker/TRACK_createUser",
      trackerUpdateUser: "mod_tracker/TRACK_updateUser",
      trackerAppStart: "mod_tracker/EVENT_appStart",

      setUserToken: "mod_user/SET_userToken",
      readUserInfo: "mod_user/GET_LOCAL_userInfo",

      setActivePageAction: "modal_pages/setActivePageAction",

      getProjects: "mod_project/getProjects",
      getProject: "mod_project/getProject",
      getDefaultModeProject: "mod_project/getDefaultModeProject",
      getModelMeta: "mod_project/getModel",

      API_getModelStatus: "mod_api/API_getModelStatus",

      cloud_userGetProfile: "mod_apiCloud/CloudAPI_userGetProfile",

      reset_network: "mod_workspace/RESET_network",
      addNetwork: "mod_workspace/ADD_network",
      chartRequestIfNeeded: "mod_workspace/SET_chartsRequestsIfNeeded",
      setUnparsedModels: "mod_workspace/SET_unparsedModels",
      setStatisticsAvailability: "mod_workspace/setStatisticsAvailability",
      setCheckpointAvailability: "mod_workspace/setCheckpointAvailability",

      getPyPiUpdate: "mod_workspace-notifications/getPyPiUpdate",

      checkRyggAvailability: "mod_api/checkRyggAvailability",
    }),
    updateOnlineStatus() {
      this.SET_onlineStatus(navigator.onLine);
    },
    disableHotKeys(event) {
      const isHotkey = isOsMacintosh() ? event.metaKey : event.ctrlKey;
      if (!isHotkey) {
        return;
      }

      switch (event.code) {
        case "KeyS":
        case "KeyG":
          event.preventDefault();
          event.stopPropagation();
          event.returnValue = false;
          break;
      }
    },
    async fetchNetworkMetas(currentProject) {
      if (
        !currentProject ||
        !currentProject.models ||
        !currentProject.models.length
      ) {
        return;
      }

      const promiseArray = currentProject.models.map(modelId =>
        this.getModelMeta(modelId),
      );

      Promise.all(promiseArray).then(metas => {
        this.fetchUnparsedModels(metas);
        this.fetchAllNetworkJsons(metas);
      });
    },
    fetchAllNetworkJsons(modelMetas) {
      if (!modelMetas) {
        return;
      }

      const promiseArray = [];
      const filteredMetas = modelMetas
        .filter(x => x.location)
        .filter(x => !this.networksWithChanges.includes(x.model_id));

      for (const fm of filteredMetas) {
        promiseArray.push(rygg_getModelJsonById(fm.model_id));
      }

      // console.log('fetchAllNetworkJsons filteredMetas', filteredMetas);
      Promise.all(promiseArray)
        .then(async models => {
          this.addNetworksToWorkspace(models, modelMetas);
          models.forEach(model => {
            if (model) {
              this.chartRequestIfNeeded(model.apiMeta.model_id);
              this.API_getModelStatus(model.apiMeta.model_id);
            }
          });

          this.$nextTick(() => {
            this.setStatisticsAvailability();
            this.setCheckpointAvailability();
          });
          return models;
        })
    },
    async fetchUnparsedModels(modelMetas) {
      let unparsedModels = [];
      modelMetas.forEach(async model => {
        const modelJson = await rygg_getModelJsonById(model.model_id);
        if (!modelJson) {
          unparsedModels.push(model);

          // Doing these removes explicitly because the data can be loaded from webstorage
          // The effect is that the same network can appear doubled in the Model Hub
          // Remove from workspace content
          this.deleteNetworkById(model.model_id);
        }
      });

      this.setUnparsedModels({ unparsedModels });
    },
    addNetworksToWorkspace(models, modelsApiData) {
      for (const [index, model] of models.entries()) {
        if (model) {
          if (this.unparsedModels.includes(model.networkID)) {
            return;
          }

          // update apiMeta wiht rygg meta.
          model.apiMeta = modelsApiData[index];

          const matchingApiData = modelsApiData.find(
            mad => mad.model_id === model.networkID,
          );
          if (matchingApiData) {
            model.frontendSettings = { ...(model.frontendSettings || {}) };
            model.frontendSettings.networkName = matchingApiData.name;
            model.frontendSettings.networkRootFolder = matchingApiData.location;
          }

          let newNetwork = assembleModel(
            model.datasetSettings,
            model.trainingSettings,
            model.graphSettings,
            model.frontendSettings,
          );
          this.addNetwork({ newNetwork: newNetwork, focusOnNetwork: false });
        }
      }

      this.$store.commit("mod_workspace/get_lastActiveTabFromLocalStorage");
    },

    serViewType() {
      const viewType = localStorage.getItem(
        LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY,
      );

      this.setViewTypeMutation(viewType);
    },

    initIntercom() {
      this.$intercom.update({
        name: this.email,
        email: this.email,
      });
    },
  },
};
</script>

<style lang="scss">
@import "scss/global";
#app {
  height: 100vh;
  display: grid;
  grid-template-areas: "header" "page";
  grid-template-rows: auto 1fr;
  grid-template-columns: 1fr;
  background: $bg-window;
  position: relative;
}
.app-header {
  position: relative;
  z-index: 13;
  grid-area: header;
  -webkit-app-region: drag;
  .btn {
    -webkit-app-region: no-drag;
  }
}
.app-page {
  grid-area: page;
}

.flex-1 {
  flex: 1;

  background-color: theme-var($neutral-7);
  border-radius: 15px 0px 0px 0px;
}
</style>
