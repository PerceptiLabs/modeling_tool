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
    router-view.app-page
    update-popup(v-if="isElectron") 
    the-info-popup(v-if="showPopup")
    confirm-popup
    modal-pages-engine
</template>

<script>
  import { isWeb, isElectron, isOsMacintosh } from "@/core/helpers";
  let ipcRenderer = null;
  if(isElectron()) {
    const electron = require('electron');
    ipcRenderer = electron.ipcRenderer;

  }
  import Analytics from '@/core/analytics';

  import { mapMutations, mapActions, mapGetters } from 'vuex';

  import HeaderLinux    from '@/components/header/header-linux.vue';
  import HeaderWin      from '@/components/header/header-win.vue';
  import HeaderMac      from '@/components/header/header-mac.vue';
  import UpdatePopup    from '@/components/global-popups/update-popup/update-popup.vue'
  import TheInfoPopup   from "@/components/global-popups/the-info-popup.vue";
  import ConfirmPopup   from "@/components/global-popups/confirm-popup.vue";
  import ModalPagesEngine from '@/components/modal-pages-engine';
  import { MODAL_PAGE_PROJECT } from '@/core/constants.js';

  export default {
    name: 'TheApp',
    components: {
      ModalPagesEngine,
      HeaderLinux, HeaderWin, HeaderMac,
      UpdatePopup, TheInfoPopup, ConfirmPopup
    },
    created() {
      window.addEventListener('online',  this.updateOnlineStatus);
      window.addEventListener('offline', this.updateOnlineStatus);
      this.trackerInit();
      this.readUserInfo();
    },
    mounted() {
      if(localStorage.hasOwnProperty('targetProject')) {
        const targetProjectId = parseInt(localStorage.getItem('targetProject'));
        this.loadProjectFromLocalStorage(targetProjectId)
        // get all project and set current one in page title
        this.getProjects()
          // .then(({data: { results: projects }}) => {
          //   if(targetProjectId) {
          //     const targetProject = projects.filter(project => project.project_id === targetProjectId)[0];
          //     this.setPageTitleMutation(`${targetProject.name} / Models`);
          //   }
          // })
      } else {
        this.setActivePageAction(MODAL_PAGE_PROJECT);
      }
      
      // @todo fetch models for project;
      if(isWeb()) {
        this.updateOnlineStatus();
        this.SET_appVersion(process.env.PACKAGE_VERSION);
        this.$store.dispatch('mod_api/API_runServer', null, {root: true});
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
      this.checkLocalToken();
      this.$store.dispatch('mod_api/API_runServer', null, {root: true});
      // this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage');
      Analytics.hubSpot.identifyUser(this.userEmail);
      this.$nextTick(() =>{
      //   if(this.userId === 'Guest') {
      //     this.$store.dispatch('mod_tracker/TRACK_initMixPanelUser', this.userId);
      //   }
      //   //this.appReady();
        this.sendPathToAnalist(this.$route.fullPath);
      })
      if(!this.user) this.cloud_userGetProfile();
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
        user: 'mod_user/GET_userProfile'
      }),
      platform() {
        return this.$store.state.globalView.platform
      },
      showNotAvailable() {
        return this.$store.state.mod_autoUpdate.showNotAvailable
      },
      // userToken() {
      //   return this.$store.state.mod_user.userToken
      // },
      userId() {
        return this.$store.getters['mod_user/GET_userID']
      },
      userEmail() {
        return this.$store.getters['mod_user/GET_userEmail']
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

        if (GET_userIsLogin && ['home', 'app', 'projects'].includes(this.$route.name)) { 
          return true; 
        }

        return false;
      }
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

          this.$store.dispatch('mod_tracker/TRACK_initMixPanelUser', newVal);
        }
        this.initUser();
      }
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
        loadProjectFromLocalStorage: 'mod_workspace/get_workspacesFromLocalStorage',
        // setPageTitleMutation: 'globalView/setPageTitleMutation',
      }),
      ...mapActions({
        openErrorPopup:   'globalView/GP_infoPopup',
        SET_onlineStatus: 'globalView/SET_onlineStatus',

        trackerInit:      'mod_tracker/TRACK_initMixPanel',
        trackerInitUser:  'mod_tracker/TRACK_initMixPanelUser',
        trackerCreateUser:'mod_tracker/TRACK_createUser',
        trackerUpdateUser:'mod_tracker/TRACK_updateUser',
        trackerAppStart:  'mod_tracker/EVENT_appStart',

        eventAppClose:    'mod_events/EVENT_appClose',
        eventAppMinimize: 'mod_events/EVENT_appMinimize',
        eventAppMaximize: 'mod_events/EVENT_appMaximize',

        setUserToken:     'mod_user/SET_userToken',
        readUserInfo:     'mod_user/GET_LOCAL_userInfo',

        setActivePageAction: 'modal_pages/setActivePageAction',
        getProjects : 'mod_project/getProjects',
        cloud_userGetProfile:     'mod_apiCloud/CloudAPI_userGetProfile',
      }),
      updateOnlineStatus() {
        this.SET_onlineStatus(navigator.onLine);
      },
      initUser() {
        this.trackerInitUser(this.userId)
          .then(()=> {
            if(this.userId !== 'Guest') {
              this.trackerCreateUser(this.userEmail);
              this.trackerUpdateUser(this.userEmail);
            }
          })
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
      checkLocalToken() {
        let localUserToken = JSON.parse(localStorage.getItem('currentUser'));
        if(localUserToken) {
          this.setUserToken(localUserToken);
          if(['home', 'login', 'register'].includes(this.$router.history.current.name)) {
            this.$router.replace({name: 'projects'});
          }
        } else {
          this.$router.push({name: 'register'}).catch(err => {});
        }
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
  }
  .app-header {
    position: relative;
    z-index: 12;
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
</style>
