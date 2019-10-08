<template lang="pug">
  #app
    header-win.app-header(
      v-if="platform === 'win32'"
      @app-closed="appClose"
      @app-minimized="appMinimize"
      @app-maximized="appMaximize"
    )
    header-mac.app-header(
      v-if="platform === 'darwin' && showMacHeader"
    )
    header-linux.app-header(
      v-if="platform === 'linux'"
      @app-closed="appClose"
      @app-minimized="appMinimize"
      @app-maximized="appMaximize"
    )
    router-view.app-page
    update-popup
    the-info-popup(v-if="isShowPopup")
    confirm-popup
</template>

<script>
  import {ipcRenderer}  from 'electron'
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
      this.trackerInit();
      this.readUserInfo();
    },
    mounted() {
      /*Menu*/
      ipcRenderer.on('get-app-version', (event, data)=> this.SET_appVersion(data));

      /*Auto update*/
      ipcRenderer.on('checking-for-update', (event, updateInfo)=> this.SET_updateInfo(updateInfo));
      ipcRenderer.on('update-available', (event, updateInfo)=> {
        //console.log('update-available', updateInfo);
        this.$nextTick(()=> {
          this.SET_showPopupUpdates(true);
          this.SET_updateInfo(updateInfo)
        })
      });
      ipcRenderer.on('update-not-available', (event, update)=> {
        //console.log('update-not-available', update);
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
      ipcRenderer.on('info',            (event, data)=> { console.log(data); });
      ipcRenderer.on('show-restore-down-icon', (event, value)=> this.SET_appIsFullView(value));

      this.calcAppPath();
      this.checkLocalToken();
      this.$nextTick(()=> {
        //if(this.userId === 'Guest') this.trackerInitUser(this.userId);
        this.appReady();
        this.sendPathToAnalist(this.$route.fullPath);
      })
    },
    data() {
      return {
        showMacHeader: true
      }
    },
    computed: {
      platform() {
        return this.$store.state.globalView.platform
      },
      showNotAvailable() {
        return this.$store.state.mod_autoUpdate.showNotAvailable
      },
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
      isShowPopup() {
        return this.errorPopup.length || this.infoPopup.length
      },
    },
    watch: {
      '$route': {
        handler(to) {
          this.sendPathToAnalist(to.fullPath)
        }
      },
      userId() {
        this.initUser()
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
          ipcRenderer.send('change-route', {path, id: this.userId})
        }
      },
      appReady() {
        const splash = document.getElementById('splashscreen');
        setTimeout(()=> {
          ipcRenderer.send('app-ready');
          splash.remove();
          document.body.className = "";
          this.trackerAppStart();
        }, 1000)
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
          if(this.$router.history.current.name === 'login') {
            this.$router.replace({name: 'projects'});
          }
        }
        else this.trackerInitUser(this.userId)
      },
      /*Header actions*/
      appClose() {
        this.eventAppClose();
      },
      appMinimize() {
        this.eventAppMinimize();
      },
      appMaximize() {
        this.eventAppMaximize();
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
