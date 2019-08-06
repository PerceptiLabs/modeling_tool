<template lang="pug">
  //-#app(
    v-hotkey="keymap"
    )
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
    the-info-popup
</template>

<script>
  import {ipcRenderer}  from 'electron'

  import HeaderLinux    from '@/components/header/header-linux.vue';
  import HeaderWin      from '@/components/header/header-win.vue';
  import HeaderMac      from '@/components/header/header-mac.vue';
  import updatePopup    from '@/components/global-popups/update-popup/update-popup.vue'
  import TheInfoPopup   from "@/components/global-popups/the-info-popup.vue";

  export default {
    name: 'TheApp',
    components: { HeaderLinux, HeaderWin, HeaderMac, updatePopup, TheInfoPopup },
    created() {
      this.$store.dispatch('mod_tracker/TRACK_initMixPanel');
    },
    mounted() {
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
      this.checkToken();
      this.$nextTick(() =>{
        if(this.userId === 'Guest') {
          this.$store.dispatch('mod_tracker/TRACK_initMixPanelUser', this.userId);
        }
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
      // userToken() {
      //   return this.$store.state.mod_user.userToken
      // },
      userId() {
        return this.$store.getters['mod_user/GET_userID']
      }
    },
    watch: {
      '$route': {
        handler(to, from) {
          this.sendPathToAnalist(to.fullPath)
        }
      },
      userId(newVal) {
        this.$store.dispatch('mod_tracker/TRACK_initMixPanelUser', newVal);
      }
    },
    methods: {
      sendPathToAnalist(path) {
        if(process.env.NODE_ENV === 'production') {
          ipcRenderer.send('change-route', {path, id: this.userId})
        }
      },
      appReady() {
        ipcRenderer.send('app-ready');
        const splash = document.getElementById('splashscreen');
        setTimeout(()=>{
          splash.remove();
          document.body.className = "";
          this.$store.dispatch('mod_tracker/EVENT_appStart');
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
        this.$store.commit('globalView/SET_appPath', path);
      },
      checkToken() {
        let localUserToken = localStorage.getItem('userToken');
        if(localUserToken) {
          this.$store.dispatch('mod_user/SET_userToken', localUserToken);
          if(this.$router.history.current.name === 'login') {
            this.$router.replace({name: 'projects'});
          }
        }
      },
      /*Header actions*/
      appClose() {
        this.$store.dispatch('mod_events/EVENT_appClose');
      },
      appMinimize() {
        this.$store.dispatch('mod_events/EVENT_appMinimize');
      },
      appMaximize() {
        this.$store.dispatch('mod_events/EVENT_appMaximize');
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
