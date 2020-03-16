<template lang="pug">
  #app
    header-win.app-header(
      v-if="platform === 'win32' || isWeb"
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
    the-info-popup(v-if="isShowPopup")
    confirm-popup
</template>

<script>
  import { isWeb, isElectron } from "@/core/helpers";
  let ipcRenderer = null;
  if(isElectron()) {
    const electron = require('electron');
    ipcRenderer = electron.ipcRenderer;

  }
  import Analytics from '@/core/analytics';

  import { mapMutations, mapActions } from 'vuex';

  import HeaderLinux    from '@/components/header/header-linux.vue';
  import HeaderWin      from '@/components/header/header-win.vue';
  import HeaderMac      from '@/components/header/header-mac.vue';
  import UpdatePopup    from '@/components/global-popups/update-popup/update-popup.vue'
  import TheInfoPopup   from "@/components/global-popups/the-info-popup.vue";
  import ConfirmPopup   from "@/components/global-popups/confirm-popup.vue";

  export default {
    name: 'TheApp',
    components: {
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
      if(this.isElectron) {
        this.appReady();
      }
      this.updateOnlineStatus();
      // this.checkUserID();
      /*Menu*/
      ipcRenderer.on('get-app-version', (event, data) => {
        this.$store.commit('globalView/SET_appVersion', data);
      });

      /*Auto update*/
      ipcRenderer.on('checking-for-update', (event, updateInfo) => {
        //console.log('checking-for-update', updateInfo);
        this.$store.commit('mod_autoUpdate/SET_updateInfo', updateInfo)
      });
      ipcRenderer.on('update-available', (event, updateInfo) => {
        //console.log('update-available', updateInfo);
        this.$nextTick(()=>{
          this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', true);
          this.$store.commit('mod_autoUpdate/SET_updateInfo', updateInfo);
        })
      });
      ipcRenderer.on('update-not-available', (event, update) => {
        //console.log('update-not-available', update);
        if(this.showNotAvailable) {
          this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', true);
          this.$store.commit('mod_autoUpdate/SET_updateStatus', 'not update')
        }
      });
      ipcRenderer.on('update-downloading', (event, percent) => {
        //console.log('update-downloading', percent);
        this.$store.commit('mod_autoUpdate/SET_updateProgress', Math.round(percent));
      });
      ipcRenderer.on('update-completed', (event, percent) => {
        //console.log('update-completed', percent);
        this.$store.commit('mod_autoUpdate/SET_updateStatus', 'done')
      });
      ipcRenderer.on('update-error', (event, error) => {
        //console.log('update-error', error);
        this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', false);
        if(error.code) this.$store.dispatch('globalView/GP_infoPopup', error.code);
      });

      ipcRenderer.on('show-mac-header', (event, value) => { this.showMacHeader = value });
      ipcRenderer.on('info',            (event, data) => { console.log(data); });
      ipcRenderer.on('show-restore-down-icon', (event, value) => {
        this.$store.commit('globalView/SET_appIsFullView', value);
      });

      this.calcAppPath();
      this.checkLocalToken();
      this.$store.dispatch('mod_api/API_runServer', null, {root: true});
      this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage');
      this.$nextTick(() =>{
        if(this.userId === 'Guest') {
          this.$store.dispatch('mod_tracker/TRACK_initMixPanelUser', this.userId);
        }
        //this.appReady();
        //this.sendPathToAnalist(this.$route.fullPath);
      })
    },
    beforeDestroy() {
      window.removeEventListener('online',  this.updateOnlineStatus);
      window.removeEventListener('offline', this.updateOnlineStatus);
    },
    data() {
      return {
        showMacHeader: true,
        isWeb: isWeb(),
        isElectron: isElectron(),
      }
    },
    computed: {
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
      isShowPopup() {
        return this.errorPopup.length || this.infoPopup.length || this.corePopup;
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

          this.$store.dispatch('mod_tracker/TRACK_initMixPanelUser', newVal);
        }
        if(this.isElectron) {
          this.initUser()
        }

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
          document.body.className = "";
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
        if(localStorage.getItem('currentUser') === 'undefined') {
          return;
        }
        let localUserToken = JSON.parse(localStorage.getItem('currentUser'));
        if(localUserToken) {
          this.setUserToken(localUserToken);
          if(this.$router.history.current.name === 'login') {
            this.$router.replace({name: 'projects'});
          }
        }
        else this.trackerInitUser(this.userId)
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
    z-index: 100;
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
