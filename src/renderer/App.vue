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
        showMacHeader: true
      }
    },
    mounted() {

      /*Menu*/
      ipcRenderer.on('get-app-version', (event, data) => {
        this.$store.commit('globalView/SET_appVersion', data)
      });

      /*Auto update*/
      ipcRenderer.on('checking-for-update', (event, updateInfo) => {
        console.log('checking-for-update', updateInfo);
        this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', true);
        this.$store.commit('mod_autoUpdate/SET_updateInfo', update)
      });
      ipcRenderer.on('update-available', (event, updateInfo) => {
        console.log('update-available', updateInfo);
        this.$nextTick(()=>{
          this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', true);
          this.$store.commit('mod_autoUpdate/SET_updateInfo', updateInfo);
        })
      });
      ipcRenderer.on('update-not-available', (event, update) => {
        console.log('update-not-available', update);
        if(this.showNotAvailable) {
          this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', true);
          this.$store.commit('mod_autoUpdate/SET_updateStatus', 'not update')
        }
      });
      ipcRenderer.on('update-downloading', (event, percent) => {
        console.log('update-downloading', percent);
        this.$store.commit('mod_autoUpdate/SET_updateProgress', Math.round(percent));
      });
      ipcRenderer.on('update-completed', (event, percent) => {
        console.log('update-completed', percent);
        this.$store.commit('mod_autoUpdate/SET_updateStatus', 'done')
      });
      ipcRenderer.on('update-error', (event, error) => {
        console.log('update-error', error);
        this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', false);
        if(error.code) this.$store.dispatch('globalView/GP_infoPopup', error.code);
      });

      ipcRenderer.on('show-mac-header', (event, value) => { this.showMacHeader = value });
      ipcRenderer.on('info',            (event, data) => { console.log(data); });

      this.calcAppPath();
      this.checkToken();
      this.$nextTick(()=>{
        this.appReady();
        this.sendPathToAnalist(this.$route.fullPath);
      })
    },
    computed: {
      // keymap () {
      //   return {
      //     'del': this.HC_delete,
      //     'backspace+meta': this.HC_delete,
      //     'ctrl+g': this.HC_addLayerContainer,
      //     'ctrl+shift+g': this.HC_unGroupLayerContainer,
      //
      //     'ctrl+n': this.HC_netNew,
      //     'ctrl+o': this.HC_netOpen,
      //     'ctrl+s': this.HC_netSave,
      //     'ctrl+shift+s': this.HC_netSaveAs,
      //     'ctrl+f4': this.HC_logOut,
      //     'ctrl+q': this.HC_closeApp,
      //     'ctrl+c': this.HC_copy,
      //     'ctrl+v': this.HC_paste,
      //     'ctrl+a': this.HC_selectAll,
      //     'ctrl+shift+a': this.HC_unselectAll,
      //     'ctrl+w': this.HC_stopExe,
      //   }
      // },
      platform() {
        return this.$store.state.globalView.platform
      },
      eventLoadNetwork() {
        return this.$store.state.mod_events.openNetwork
      },
      showNotAvailable() {
        return this.$store.state.mod_autoUpdate.showNotAvailable
      },
      userToken() {
        return this.$store.state.globalView.userToken
      },
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
          ipcRenderer.send('change-route', {path, id: this.userToken})
        }
      },
      appReady() {
        ipcRenderer.send('app-ready');
        const splash = document.getElementById('splashscreen');
        setTimeout(()=>{
          splash.remove();
          document.body.className = "";
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
        let localUserToken = localStorage.getItem('userId');
        if(localUserToken) {
          this.$store.dispatch('globalView/SET_userToken', localUserToken);
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
