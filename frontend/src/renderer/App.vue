<template lang="pug">
  #app
    header-win.app-header(
      v-if="platform === 'win32' || (showMenuBar && isWeb) "
      @app-closed="appClose"
      @app-minimized="appMinimize"
      @app-maximized="appMaximize"
    )
    header-mac.app-header(
      v-if="platform === 'darwin' && showMacHeader && isElectron"
    )
      header-linux.app-header(
        v-if="platform === 'linux' && isElectron"
        @app-closed="appClose"
        @app-minimized="appMinimize"
        @app-maximized="appMaximize"
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

  let ipcRenderer = null;
  if(isElectron()) {
    const electron = require('electron');
    ipcRenderer = electron.ipcRenderer;

  }
  import Analytics from '@/core/analytics';
  import { LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY } from '@/core/constants.js'

  import { mapMutations, mapActions, mapGetters } from 'vuex';
  import ProjectSidebar         from '@/pages/layout/project-sidebar.vue';
  import HeaderLinux            from '@/components/header/header-linux.vue';
  import HeaderWin              from '@/components/header/header-win.vue';
  import HeaderMac              from '@/components/header/header-mac.vue';
  import UpdatePopup            from '@/components/global-popups/update-popup/update-popup.vue'
  import PiPyPopupUpdate        from "@/components/global-popups/update-popup/pipy-update-popup.vue";  
  import TheInfoPopup           from "@/components/global-popups/the-info-popup.vue";
  import ConfirmPopup           from "@/components/global-popups/confirm-popup.vue";
  import DeleteConfirmPopup     from "@/components/global-popups/delete-confirm-popup.vue";
  import ModalPagesEngine       from '@/components/modal-pages-engine.vue';
  import AboutAppPopup           from "@/components/global-popups/about-app-popup.vue";
  import { MODAL_PAGE_PROJECT, MODAL_PAGE_WHATS_NEW, MODAL_PAGE_QUESTIONNAIRE } from '@/core/constants.js';

  export default {
    name: 'TheApp',
    components: {
      ProjectSidebar,
      ModalPagesEngine,
      HeaderLinux, HeaderWin, HeaderMac,
      UpdatePopup, TheInfoPopup, ConfirmPopup, DeleteConfirmPopup, CreateIssuePopup, PiPyPopupUpdate, AboutAppPopup,
      TutorialsChecklist, TutorialNotification
    },
    created() {
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
      this.$store.commit('mod_workspace-changes/get_workspaceChangesInLocalStorage');

      this.$store.dispatch('mod_tutorials/loadTutorialProgress')
        .then(() => {
          if (this.isUserFirstLogin) {
            if (!process.env.NO_KC){
              this.setActivePageAction(MODAL_PAGE_QUESTIONNAIRE);
            }
          } else if (!this.getHasShownWhatsNew) {
            this.setActivePageAction(MODAL_PAGE_WHATS_NEW);
          } else {
            this.initTutorialView();
          }
        });      

      this.$store.dispatch('mod_tutorials/activateNotification');

      // @todo fetch models for project;
      if(isWeb()) {
        this.updateOnlineStatus();
        this.SET_appVersion(process.env.PACKAGE_VERSION);
        this.$store.dispatch('mod_api/API_runServer', null, {root: true});
        document.body.style.overflow = 'hidden';
        document.addEventListener('keydown', this.disableHotKeys);
      } else {
        this.appReady();
        this.updateOnlineStatus();
        /*Menu*/
        ipcRenderer.on('get-app-version', (event, data)=> this.SET_appVersion(data));

        /*Auto update*/
        ipcRenderer.on('checking-for-update', (event, updateInfo)=> this.SET_updateInfo(updateInfo));
        ipcRenderer.on('update-available', (event, updateInfo)=> {
          this.$nextTick(()=> {
            this.SET_showPopupUpdates(true);
            this.SET_updateInfo(updateInfo)
          })
        });
        ipcRenderer.on('update-not-available', (event, update)=> {
          if(this.showNotAvailable) {
            this.SET_showPopupUpdates(true);
            this.SET_updateStatus('not update')
          }
        });
        ipcRenderer.on('update-downloading', (event, percent)=> this.SET_updateProgress(Math.round(percent)));
        ipcRenderer.on('update-completed', (event, percent)=> this.SET_updateStatus('done'));
        ipcRenderer.on('update-error', (event, error)=> {
          this.SET_showPopupUpdates(false);
          if(error) this.openErrorPopup(error);
        });

        ipcRenderer.on('show-mac-header', (event, value)=> { this.showMacHeader = value });
        ipcRenderer.on('info',            (event, data)=> { /*console.log(data); */});
        ipcRenderer.on('show-restore-down-icon', (event, value)=> this.SET_appIsFullView(value));

        this.calcAppPath();
      }
      this.$store.dispatch('mod_api/API_runServer', null, {root: true});
      // this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage');

      this.$nextTick(() =>{
      //   if(this.userId === 'Guest') {
      //     this.$store.dispatch('mod_tracker/TRACK_initMixPanelUser', this.userId);
      //   }
      //   //this.appReady();
        this.sendPathToAnalist(this.$route.fullPath);
      })
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
      platform() {
        return this.$store.state.globalView.platform
      },
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
      corePopup() {
        return this.$store.state.globalView.globalPopup.coreNotFoundPopup
      },
      showPopup() {
        return this.errorPopup.length || (this.infoPopup && this.infoPopup.length) || this.corePopup;
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
    },
    watch: {
      '$route': {
        handler(to, from) {
          if(this.isElectron) {
            this.sendPathToAnalist(to.fullPath);
          }
        }
      },
      userId(newVal) {
        if(this.isWeb) {
          Analytics.googleAnalytics.trackUserId(this.$store.getters['mod_user/GET_userID']);
        }
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
        SET_appPath:          'globalView/SET_appPath',

        SET_updateInfo:       'mod_autoUpdate/SET_updateInfo',
        SET_showPopupUpdates: 'mod_autoUpdate/SET_showPopupUpdates',
        SET_updateStatus:     'mod_autoUpdate/SET_updateStatus',
        SET_updateProgress:   'mod_autoUpdate/SET_updateProgress',
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

        eventAppClose:          'mod_events/EVENT_appClose',
        eventAppMinimize:       'mod_events/EVENT_appMinimize',
        eventAppMaximize:       'mod_events/EVENT_appMaximize',

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
      sendPathToAnalist(path) {
        if(process.env.NODE_ENV === 'production') {
          if(this.isElectron) {
            ipcRenderer.send('change-route', {path, id: this.userId})
          }
        }
      },
      appReady() {
        const splash = document.getElementById('splashscreen');
        setTimeout(()=> {
          if(this.isElectron) {
            ipcRenderer.send('app-ready');
          }
          splash.remove();
          document.body.classList.remove('show-splashscreen');
          this.trackerAppStart();
        }, this.isElectron ? 2000 : 1000)
      },
      calcAppPath() {
        let resPath = process.resourcesPath;
        var path = '';
        switch (process.platform) {
          case 'win32':
            path = resPath.slice(0, resPath.indexOf('resources'));
            break;
          case 'darwin':
            path = resPath.slice(0, resPath.indexOf('Resources'));
            break;
          case 'linux':
            path = resPath.slice(0, resPath.indexOf('resources'));
            break
        }
        this.SET_appPath(path);
      },
      // checkLocalToken() {
      //   let localUserToken = JSON.parse(localStorage.getItem('currentUser'));
      //   if(localUserToken) {
      //     this.setUserToken(localUserToken);
      //     if(['main-page', 'settings'].includes(this.$router.history.current.name)) {
      //       this.$router.replace({name: 'projects'});
      //     }
      //   } else {
      //     this.$router.push({name: 'main-page'}).catch(err => {});
      //   }    
      // },
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
      /*Header actions*/
      appClose() {
        if(this.isElectron) {
          this.eventAppClose();
        }
      },
      appMinimize() {
        if(this.isElectron) {
          this.eventAppMinimize();
        }
      },
      appMaximize() {
        if(this.isElectron) {
          this.eventAppMaximize();
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
