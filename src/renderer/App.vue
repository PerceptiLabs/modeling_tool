<template lang="pug">
  #app(
    v-shortkey="globalKeyEvents"
    @shortkey="switchKeyPress($event)"
  )
    header-win.app-header(
      v-if="platform === 'win32'"
      @app-closed="appClose"
      @app-minimized="appMinimize"
      @app-maximized="appMaximize"
    )
    header-mac.app-header(
      v-if="platform === 'darwin'"
      @app-closed="appClose"
      @app-minimized="appMinimize"
      @app-maximized="appMaximize"
    )
    header-linux.app-header(
      v-if="platform === 'linux'"
      @app-closed="appClose"
      @app-minimized="appMinimize"
      @app-maximized="appMaximize"
    )
    router-view.app-page
    update-popup(
      :progress="percentProgress"
      :update-info="updateInfo"
      @started-update="updateStart"
      @restart-app="restartApp"
    )
    the-info-popup
</template>

<script>
  import {ipcRenderer}  from 'electron'
  import {openLoadDialog, loadNetwork} from '@/core/helpers.js'

  import HeaderLinux    from '@/components/header/header-linux.vue';
  import HeaderWin      from '@/components/header/header-win.vue';
  import HeaderMac      from '@/components/header/header-mac.vue';
  import updatePopup    from '@/components/global-popups/update-popup/update-popup.vue'
  import TheInfoPopup   from "@/components/global-popups/the-info-popup.vue";

  export default {
    name: 'TheApp',
    components: { HeaderLinux, HeaderWin, HeaderMac, updatePopup, TheInfoPopup },
    data() {
      return {
        percentProgress: 0,
        updateInfo: {},
        globalKeyEvents: {
          delete: ['del'],
          deleteMac: ['backspace', 'meta'],
          addLayerContainer: ['ctrl', 'g'],
        }
      }
    },
    mounted() {
      this.calcAppPath();
      this.checkToken();

      ipcRenderer.on('newNetwork', (event) => {
        this.$store.dispatch('mod_workspace/ADD_network', {'ctx': this});
      });
      ipcRenderer.on('openNetwork', (event) => {
        this.$store.commit('mod_events/set_openNetwork')
      });
      ipcRenderer.on('saveNetwork', (event) => {
        this.$store.commit('mod_events/set_saveNetwork')
      });
      ipcRenderer.on('logOut', (event) => {
        this.logOut();
      });
      ipcRenderer.on('closeApp', (event) => {
        this.appClose();
      });
      ipcRenderer.on('update-finded', (event, update) => {
        this.updateInfo = update;
        this.$store.commit('globalView/SET_showPopupUpdates', true)
      });
      ipcRenderer.on('update-not-finded', (event, update) => {
        this.$store.commit('globalView/SET_showPopupUpdates', true)
        this.$store.commit('globalView/SET_updateStatus', 'not update')
      });
      ipcRenderer.on('percent-progress', (event, percent) => {
        this.percentProgress = Math.round(percent);
      });
      ipcRenderer.on('download-completed', (event, percent) => {
        this.$store.commit('globalView/SET_updateStatus', 'done')
      });
      ipcRenderer.on('info', (event, data) => {
        console.log(data);
      });
      ipcRenderer.on('getAppVersion', (event, data) => {
        this.$store.commit('globalView/SET_appVersion', data)
      });

      this.appReady();
      this.sendPathToAnalist(this.$route.fullPath);
    },
    computed: {
      platform() {
        return this.$store.state.globalView.platform
      },
      eventLoadNetwork() {
        return this.$store.state.mod_events.openNetwork
      },
      eventLogout() {
        return this.$store.state.mod_events.logOut
      },
      showPopupUpdates() {
        return this.$store.state.globalView.globalPopup.showPopupUpdates
      },
      userToken() {
        return this.$store.state.globalView.userToken
      }
    },
    watch: {
      eventLoadNetwork() {
        let opt = {
          title:"Load Network",
          filters: [
            {name: 'Text', extensions: ['json']},
          ]
        };
        this.openLoadDialog(opt)
          .then((pathArr)=> this.loadNetwork(pathArr))
          .catch((err)=> console.error(err))
      },
      '$route': {
        handler(to, from) {
          this.sendPathToAnalist(to.fullPath)
        }
      }
    },
    methods: {
      openLoadDialog,
      loadNetwork,
      sendPathToAnalist(path) {
        if(process.env.NODE_ENV === 'production') {
          ipcRenderer.send('changeRoute', {path, id: this.userToken})
        }
      },
      appReady() {
        ipcRenderer.send('appReady');
        const splash = document.getElementById('splashscreen');
        setTimeout(()=>{
          splash.remove();
          document.body.className = "";
        }, 1000)
      },
      appClose() {
        this.$store.dispatch('mod_events/EVENT_closeApp');
      },
      appMinimize() {
        ipcRenderer.send('appMinimize')
      },
      appMaximize() {
        ipcRenderer.send('appMaximize')
      },
      updateStart() {
        ipcRenderer.send('update-start')
      },
      restartApp() {
        ipcRenderer.send('restart-app-after-update')
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
          this.$store.dispatch('globalView/SET_userToken', localUserToken);
          if(this.$router.history.current.name === 'login') {
            this.$router.replace({name: 'projects'});
          }
        }
      },
      logOut() {
        this.$store.dispatch('mod_events/EVENT_logOut', this)
      },
      switchKeyPress(event) {
        event.preventDefault();
        switch (event.srcKey) {
          case 'delete':
          case 'deleteMac':
            this.$store.dispatch('mod_events/EVENT_hotKeyDeleteElement');
            break;
          case 'addLayerContainer':
            this.$store.dispatch('mod_workspace/ADD_container');
            break;
        }
      }
    },
  }
</script>

<style lang="scss">
  @import "scss/common";
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
    z-index: 3;
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
