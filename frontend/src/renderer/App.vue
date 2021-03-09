<template lang="pug">
  #app
    app-header.app-header(
      v-if="showMenuBar"
    )
    div.d-flex.app-page
      project-sidebar
      router-view.flex-1
    update-popup(v-if="isElectron") 
    the-info-popup(v-if="showPopup")
    confirm-popup
    delete-confirm-popup
    PiPyPopupUpdate(v-if="showPiPyNotification")
    create-issue-popup(v-if="showCreateIssuesPopup")
    modal-pages-engine
    tutorials-checklist(v-if="showTutorialChecklist" :style="tutorialChecklistPosition")
    about-app-popup(v-if="showAppAboutPopUp")
    #tutorial-notifications(v-if="showTutorialNotifications")
      tutorial-notification(
        v-for="n in tutorialNotifications"
        :key="n.stepCode"
        :stepCode="n.stepCode"
        :arrowDirection="n.arrowDirection"
      )
</template>

<script>
  import { isWeb, isElectron, isOsMacintosh } from "@/core/helpers";
  import CreateIssuePopup         from '@/components/global-popups/create-issues-popup.vue';
  import TutorialsChecklist       from '@/components/tutorial/tutorial-checklist.vue';
  import TutorialNotification from "@/components/different/tutorial-notification.vue";
  import { getModelJson as fileserver_getModelJson } from '@/core/apiFileserver';
  import { fileserverAvailability } from '@/core/apiFileserver';
  import Analytics from '@/core/analytics';
  import { LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY, localStorageGridKey } from '@/core/constants.js'
  import { mapMutations, mapActions, mapGetters } from 'vuex';
  import ProjectSidebar         from '@/pages/layout/project-sidebar.vue';
  import AppHeader              from '@/components/app-header/app-header.vue';
  import UpdatePopup            from '@/components/global-popups/update-popup/update-popup.vue'
  import PiPyPopupUpdate        from "@/components/global-popups/update-popup/pipy-update-popup.vue";  
  import TheInfoPopup           from "@/components/global-popups/the-info-popup.vue";
  import ConfirmPopup           from "@/components/global-popups/confirm-popup.vue";
  import DeleteConfirmPopup     from "@/components/global-popups/delete-confirm-popup.vue";
  import ModalPagesEngine       from '@/components/modal-pages-engine.vue';
  import AboutAppPopup          from "@/components/global-popups/about-app-popup.vue";
  import { MODAL_PAGE_PROJECT, MODAL_PAGE_WHATS_NEW, MODAL_PAGE_QUESTIONNAIRE, IS_VALID_KEYCLOACK_CHECKER_URL } from '@/core/constants.js';
  import { isUrlReachable } from '@/core/apiFileserver.js';

  export default {
    name: 'TheApp',
    components: {
      ProjectSidebar,
      ModalPagesEngine,
      AppHeader,
      UpdatePopup, TheInfoPopup, ConfirmPopup, DeleteConfirmPopup, CreateIssuePopup, PiPyPopupUpdate, AboutAppPopup,
      TutorialsChecklist, TutorialNotification
    },
    beforeCreate() {
      this.$store.dispatch('mod_api/API_setAppInstance');
    },
    created() {
      window.addEventListener("beforeunload", (e) => {
        let networksHaveChanges = this.networksWithChanges.some(id=> this.getWorkspacesIds.includes(id));
        if(networksHaveChanges) { 
          const confirmationMessage = 'It looks like you have edited model.';
          
          (e || window.event).returnValue = confirmationMessage; //Gecko + IE

          return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        }
    });
      window.addEventListener('online',  this.updateOnlineStatus);
      window.addEventListener('offline', this.updateOnlineStatus);
      this.trackerInit();
      this.readUserInfo();
      this.checkFileserverAvailability();
      
      // from webstorage
      this.loadWorkspacesFromWebStorage()
        .then(_ => {
          this.$store.commit('mod_workspace/get_lastActiveTabFromLocalStorage');
          this.setStatisticsAvailability();
          this.setCheckpointAvailability();
        });

      this.$store.commit('mod_project/setIsDefaultProjectMode');
      
    },
    mounted() {
      this.getPyPiUpdate();

      if (this.isDefaultProjectMode) { 
        // in the free version, the user is locked to a single project
        this.getDefaultModeProject();
      }
      else if(localStorage.hasOwnProperty('targetProject')) {
        const targetProjectId = parseInt(localStorage.getItem('targetProject'));
        
        // this.loadProjectFromLocalStorage(targetProjectId)
        this.getProjects();
          // .then(({data: { results: projects }}) => {
          //   if(targetProjectId) {
          //     const targetProject = projects.filter(project => project.project_id === targetProjectId)[0];
          //     this.setPageTitleMutation(`${targetProject.name} / Models`);
          //   }
          // })
      } else {
        this.getProjects();
        if(localStorage.hasOwnProperty('currentUser')) {
          this.setActivePageAction(MODAL_PAGE_PROJECT);
        }
      }
      if(localStorage.hasOwnProperty(localStorageGridKey)) {
        const gridValue = localStorage.getItem(localStorageGridKey) === 'true';
        this.$store.commit('globalView/setGridStateMutation', gridValue);
      }
      this.$store.commit('mod_workspace-changes/get_workspaceChangesInLocalStorage');

      this.$store.dispatch('mod_tutorials/loadTutorialProgress')
        .then(async () => {
          if (this.isUserFirstLogin) {
            const isKeycloackReachable = await isUrlReachable(IS_VALID_KEYCLOACK_CHECKER_URL);
            if (!process.env.NO_KC && isKeycloackReachable){
              this.setActivePageAction(MODAL_PAGE_QUESTIONNAIRE);
            }

          } else if (!this.getHasShownWhatsNew) {
            this.setActivePageAction(MODAL_PAGE_WHATS_NEW);
          } else {
            this.initTutorialView();
          }
        });      

      this.$store.dispatch('mod_tutorials/activateNotification');

      this.updateOnlineStatus();
      this.SET_appVersion(process.env.PACKAGE_VERSION);
      this.$store.dispatch('mod_api/API_runServer', null, {root: true});
      document.body.style.overflow = 'hidden';
      document.addEventListener('keydown', this.disableHotKeys);
     
      this.$store.dispatch('mod_api/API_runServer', null, {root: true});
      // this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage');

      if(!this.user) this.cloud_userGetProfile();

      setTimeout(() => {
        this.$store.dispatch('mod_api/API_getOutputDim');
      }, 1000);
    },
    beforeDestroy() {
      window.removeEventListener('online',  this.updateOnlineStatus);
      window.removeEventListener('offline', this.updateOnlineStatus);
      document.removeEventListener('keydown', this.disableHotKeys);
    },
    data() {
      return {
        showMacHeader: true,
        isWeb: isWeb(),
        isElectron: isElectron(),
      }
    },
    computed: {
      ...mapGetters({
        user:                   'mod_user/GET_userProfile',
        isDefaultProjectMode:   'mod_project/GET_isDefaultProjectMode',
        currentProject:         'mod_project/GET_project',
        viewType:               'mod_workspace/GET_viewType',
        currentModelIndex:      'mod_workspace/GET_currentModelIndex',
        currentStatsIndex:      'mod_workspace/GET_currentStatsIndex',
        currentTestIndex:       'mod_workspace/GET_currentTestIndex',
        networksWithChanges:    'mod_workspace-changes/get_networksWithChanges',
        showPiPyNotification:   'mod_workspace-notifications/getPiPyShowNotification',
        getActiveNotifications: 'mod_tutorials/getActiveNotifications',
        getIsTutorialMode:      'mod_tutorials/getIsTutorialMode',
        getShowChecklist:       'mod_tutorials/getShowChecklist',
        getShowTutorialTips:    'mod_tutorials/getShowTutorialTips',
        getHasShownWhatsNew:    'mod_tutorials/getHasShownWhatsNew', 
        emptyNavigationMode:    'mod_empty-navigation/getEmptyScreenMode',
      }),
      showNotAvailable() {
        return this.$store.state.mod_autoUpdate.showNotAvailable
      },
      showNewModelPopup() {
        return this.$store.state.globalView.globalPopup.showNewModelPopup;
      },
      userId() {
        return this.$store.getters['mod_user/GET_userID']
      },
      userProfile() {
        return this.$store.getters['mod_user/GET_userProfile']
      },
      isUserFirstLogin() {
        return this.$store.getters['mod_user/GET_isUserFirstLogin'];
      },
      /*show popup*/
      infoPopup() {
        return this.$store.state.globalView.globalPopup.showInfoPopup
      },
      errorPopup() {
        return this.$store.state.globalView.globalPopup.showErrorPopup
      },
      showPopup() {
        return this.errorPopup.length || (this.infoPopup && this.infoPopup.length);
      },
      showMenuBar() {

        const GET_userIsLogin = this.$store.getters['mod_user/GET_userIsLogin']
        if (GET_userIsLogin && ['home', 'app', 'projects', 'main-page', 'settings'].includes(this.$route.name)) { 
          return true; 
        }

        return false;
      },
      showCreateIssuesPopup() {
        return this.$store.state.globalView.globalPopup.showCreateIssuesPopup;
      },
      currentPage() {
        return this.$store.state.modal_pages.currentPage
      },
      showTutorialChecklist() {
        if (!this.getIsTutorialMode) { return false; }
        if (!this.getShowChecklist) { return false; }
        
        if (this.hasModalsOpenInWorkspace) { return false; }

        if (!this.currentPage) {
          return true;
        }
        if (this.currentPage === 'MODAL_PAGE_PROJECT') {
          return true;
        }

        return false;
      },
      showTutorialNotifications() {
        // Don't show notifications if there are any overlays

        if (this.currentPage) { return false; }
        if (this.hasModalsOpenInWorkspace) { return false; }

        // have check each screen because the proposal to separate each view
        // into it's own component wasn't well received.
        if (this.$route.name === 'projects') { return this.getShowTutorialTips; }
        else if (this.viewType === 'model' && this.currentModelIndex === -1) { return false; }
        else if (this.viewType === 'statistic' && this.currentStatsIndex === -1) { return false; }
        else if (this.viewType === 'test' && this.currentTestIndex === -1) { return false; }

        return this.getIsTutorialMode && this.getShowTutorialTips;
      },
      hasModalsOpenInWorkspace() {
        return (
          this.$store.state.globalView.globalPopup.showNetResult ||
          this.$store.state.globalView.globalPopup.showWorkspaceBeforeImport ||
          this.$store.state.globalView.globalPopup.showCoreSideSettings ||
          this.$store.state.globalView.globalPopup.showFilePickerPopup ||
          this.$store.state.globalView.globalPopup.showLoadSettingPopup ||
          this.$store.state.globalView.globalPopup.showSaveNetworkPopup ||
          this.$store.state.globalView.globalPopup.showExportNetworkPopup ||
          this.$store.state.globalView.globalPopup.showExportNetworkPopup ||
          this.$store.state.globalView.globalPopup.showExportNetworkToGitHubPopup ||
          this.$store.state.globalView.globalPopup.showImportNetworkfromGitHubOrLocalPopup ||
          this.showCreateIssuesPopup ||
          this.showPopup
        );

      },
      currentNetworkId() {
        return this.$store.getters['mod_workspace/GET_currentNetworkId'];
      },
      unparsedModels() {
        return this.$store.state.mod_workspace.unparsedModels
          .map(m => m.model_id);
      },
      tutorialNotifications() {
        return this.getActiveNotifications;
      },
      tutorialChecklistPosition() {

        let rightValueRm = 1;
        let bottomValueRm = 1;

        if (this.$route.name !== 'projects' &&
            this.$route.name !== 'settings' &&
            this.emptyNavigationMode === 0 &&
            !this.showNewModelPopup) {
          
          bottomValueRm += 2; // the-workspace
          bottomValueRm += 1; // scrollbars

          if (this.$store.state.globalView.hideSidebar) {
            rightValueRm += 25; // hardcoded in the-sidebar.vue file
          }

          let isNotificationWindowOpen = this.$store.getters['mod_workspace-notifications/getNotificationWindowState'](this.currentNetworkId);

          if (isNotificationWindowOpen) {
            rightValueRm += 70; // hardcoded in the workspace-code-window.vue file
          }

          const toasts = this.$store.getters['mod_workspace-notifications/getToasts'](this.currentNetworkId);
          if (toasts) {
            const errorToast = toasts.find(t => t.type === 'error');
            const warningToast = toasts.find(t => t.type === 'error');

            if ((errorToast && errorToast.count) || (warningToast && errorToast.warningToast)) {
              rightValueRm += 21; // hardcoded in the the-toaster.vue file
            }
          }
        }

        return { 
          right: `${rightValueRm}rem`,
          bottom: `${bottomValueRm}rem`
        };
      },
      showAppAboutPopUp() {
        return this.$store.state.globalView.globalPopup.showAppAbout;
      },
      getWorkspacesIds() {
        return this.$store.state['mod_workspace'].workspaceContent.map(workspace => workspace.networkID.toString());
      }
    },
    watch: {
      userId(newVal) {
        Analytics.googleAnalytics.trackUserId(this.$store.getters['mod_user/GET_userID']);
      },
      userProfile(newVal) {
        if (!newVal || newVal.email === 'Guest') { return; }

        setTimeout(() => {
          this.trackerCreateUser(newVal);
          this.trackerUpdateUser(newVal);
          this.trackerInitUser(newVal);
        }, 5000);
      },
      currentProject: {
        immediate: true,
        deep: true,
        handler(newVal, oldVal) {
          // Used to have an if statement to not load if there are unsaved changes,
          // this is now use but filtering out the networksWithChanges in the
          // fetchAllNetworkJsons function

          if (this.isDefaultProjectMode && (!newVal || !newVal.name || newVal.name !== 'Default')) { return; }
          // using this function because the watcher can be aggressive with changes
          if(!isSameProject(newVal,oldVal)) {
            this.reset_network();
            this.deleteAllIds();
            this.fetchNetworkMetas(newVal);
          }

          function isSameProject(project1, project2) {
            if (!project1 && !project2) { return true; }
            if (project1 && !project2) { return false; }
            if (!project1 && project2) { return false; }
            if (project1.name !== project2.name)  { return false; }
            // if (project1.models.length !== project2.models.length)  { return false; }
            // if (
            //   project1.models.every(p1 => !project2.models.includes(p1)) ||
            //   project2.models.every(p2 => !project1.models.includes(p2)))  { return false; }

            return true;
          }
        }
      },
    },
    methods: {
      ...mapMutations({
        SET_appVersion:       'globalView/SET_appVersion',
        SET_appIsFullView:    'globalView/SET_appIsFullView',

        // loadProjectFromLocalStorage: 'mod_workspace/get_workspacesFromLocalStorage',
        // setPageTitleMutation: 'globalView/setPageTitleMutation',

        deleteNetworkById:    'mod_workspace/delete_networkById',
        setViewTypeMutation:  'mod_workspace/setViewTypeMutation'
      }),
      ...mapActions({
        openErrorPopup:         'globalView/GP_infoPopup',
        SET_onlineStatus:       'globalView/SET_onlineStatus',

        trackerInit:            'mod_tracker/TRACK_initMixPanel',
        trackerInitUser:        'mod_tracker/TRACK_initMixPanelUser',
        trackerCreateUser:      'mod_tracker/TRACK_createUser',
        trackerUpdateUser:      'mod_tracker/TRACK_updateUser',
        trackerAppStart:        'mod_tracker/EVENT_appStart',

        setUserToken:           'mod_user/SET_userToken',
        readUserInfo:           'mod_user/GET_LOCAL_userInfo',

        setActivePageAction:    'modal_pages/setActivePageAction',

        getProjects :           'mod_project/getProjects',
        createProject:          'mod_project/createProject',
        getDefaultModeProject:  'mod_project/getDefaultModeProject',
        getModelMeta:           'mod_project/getModel',
        
        API_getModelStatus:     'mod_api/API_getModelStatus',

        cloud_userGetProfile:   'mod_apiCloud/CloudAPI_userGetProfile',
        
        loadWorkspacesFromWebStorage:   'mod_webstorage/loadWorkspaces',

        reset_network:            'mod_workspace/RESET_network',
        addNetwork:               'mod_workspace/ADD_network',
        setUnparsedModels:        'mod_workspace/SET_unparsedModels',
        setStatisticsAvailability:'mod_workspace/setStatisticsAvailability',
        setCheckpointAvailability:'mod_workspace/setCheckpointAvailability',

        deleteId:            'mod_webstorage/deleteId',
        deleteAllIds:        'mod_webstorage/deleteAllIds',        
        updateWorkspaces:    'mod_webstorage/updateWorkspaces',

        getPyPiUpdate:          'mod_workspace-notifications/getPyPiUpdate',

        setCurrentView:         'mod_tutorials/setCurrentView',
      }),
      updateOnlineStatus() {
        this.SET_onlineStatus(navigator.onLine);
      },
      checkFileserverAvailability() {
        fileserverAvailability().then(resp => {
          if (resp === "UNAVAILABLE") {
            this.openErrorPopup("The file server isn't available");
          } else if (resp === "BAD_TOKEN") {
            this.openErrorPopup("Unable to talk to the file server. Did you use the correct token to load this page?");
          }
        })
      },
      disableHotKeys(event) {
        const isHotkey = isOsMacintosh() ? event.metaKey : event.ctrlKey;
        if (!isHotkey) { 
          return; 
        }

        switch (event.code) {
          case 'KeyS':
          case 'KeyG':
              event.preventDefault();
              event.stopPropagation();
              event.returnValue = false;
              break;
        }
      },
      async fetchNetworkMetas(currentProject) {
        if (!currentProject || !currentProject.models || !currentProject.models.length) { return; }

        const promiseArray = 
          currentProject.models
            .map(x => this.getModelMeta(x));

        Promise.all(promiseArray)
          .then(metas => {
            this.fetchUnparsedModels(metas);
            this.fetchAllNetworkJsons(metas);
          });
      },
      fetchAllNetworkJsons(modelMetas) {
        
        if (!modelMetas) { return; }

        const promiseArray = []
        const filteredMetas = modelMetas
            .filter(x => x.location)
            .filter(x => !this.networksWithChanges.includes(x.model_id));

        for (const fm of filteredMetas) {
          promiseArray.push(fileserver_getModelJson(fm.location + '/model.json'));
        }
        
        // console.log('fetchAllNetworkJsons filteredMetas', filteredMetas);
        Promise.all(promiseArray)
          .then(models => {
            // console.log('fetchAllNetworkJsons models', models);
            this.addNetworksToWorkspace(models, modelMetas);
            models.forEach(model => {
              if (model) {
                this.API_getModelStatus(model.networkID);
              }
            });

            this.$nextTick(() => {
              this.setStatisticsAvailability();
              this.setCheckpointAvailability();
            });
          });
      },
      async fetchUnparsedModels(modelMetas){
        let unparsedModels = [];

        modelMetas.forEach(async (model) => {
          const modelJson = await fileserver_getModelJson(model.location + '/model.json');
          if(!modelJson) {
            unparsedModels.push(model);
            
            // Doing these removes explicitly because the data can be loaded from webstorage
            // The effect is that the same network can appear doubled in the Model Hub
            // Remove from workspace content
            this.deleteNetworkById(model.model_id);
            // Remove from webstorage
            this.deleteId(model.model_id);
          }
        });

        this.setUnparsedModels({unparsedModels});
      },
      addNetworksToWorkspace(models, modelsApiData) {
        for(const [index, model] of models.entries()) {
          if(model) { 
            if (this.unparsedModels.includes(model.networkID)) { return; }

            // update apiMeta wiht rygg meta.
            model.apiMeta = modelsApiData[index];

            const matchingApiData = modelsApiData.find(mad => mad.model_id === model.networkID);
            if (matchingApiData) {
              model.networkName = matchingApiData.name;
              model.networkRootFolder = matchingApiData.location;
            }
            this.addNetwork({network: model, apiMeta: model.apiMeta, focusOnNetwork: false});

           }
        }

        // Commented out because addNetwork already calls updateWorkspaces
        // this.updateWorkspaces();
      },
    
      initTutorialView() {
        const viewType = localStorage.getItem(LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY);

        // for the project side bar
        this.setViewTypeMutation(viewType);

        // for the tutorial
        if (this.$route.name === 'projects') { 
          this.setCurrentView('tutorial-model-hub-view');
        } else if (viewType === 'model') {
          this.setCurrentView('tutorial-workspace-view');
        } else if (viewType === 'statistic') {
          this.setCurrentView('tutorial-statistics-view');
        } else if (viewType === 'test') {
          this.setCurrentView('tutorial-test-view');
        }
      }
    },
  }
</script>

<style lang="scss">
  @import "scss/global";
  #app {
    height: 100vh;
    display: grid;
    grid-template-areas: 'header' 'page';
    grid-template-rows: auto 1fr;
    grid-template-columns: 1fr;
    overflow: hidden;
    background: #27292F;
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
    overflow: hidden;
  }
  
  .flex-1 {
    flex: 1;
  }
</style>
