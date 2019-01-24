<template lang="pug">
  #app
    header-win.app-header(
      v-if="platform === 'win32'"
      @appClosed="appClose"
      @appMinimized="appMinimize"
      @appMaximized="appMaximize"
    )
    header-mac.app-header(
      v-if="platform === 'darwin'"
      @appClosed="appClose"
      @appMinimized="appMinimize"
      @appMaximized="appMaximize"
    )
    header-linux.app-header(
      v-if="platform === 'linux'"
      @appClosed="appClose"
      @appMinimized="appMinimize"
      @appMaximized="appMaximize"
    )
    router-view.app-page
</template>

<script>
  import {ipcRenderer}  from 'electron'

  export default {
    name: 'quantumnet',
    components: {
      HeaderLinux: () => import ('@/components/header/header-linux.vue'),
      HeaderWin: () => import ('@/components/header/header-win.vue'),
      HeaderMac: () => import ('@/components/header/header-mac.vue'),
      },
    mounted() {
      //main process events
      ipcRenderer.on('newNetwork', (event) => {
        this.$store.dispatch('mod_workspace/ADD_network');
      });
      ipcRenderer.on('openNetwork', (event) => {
        this.$store.commit('mod_events/set_openNetwork')
      });
      ipcRenderer.on('saveNetwork', (event) => {
        this.$store.commit('mod_events/set_saveNetwork')
      });
      ipcRenderer.on('closeApp', (event) => {
        this.appClose();
      });
      ipcRenderer.on('info', (event, data) => {
        console.log(data);
      });
      ipcRenderer.send('appReady');
    },
    methods: {
      appClose() {
        this.$store.dispatch('mod_events/EVENT_closeCore');
      },
      appMinimize() {
        ipcRenderer.send('appMinimize')
      },
      appMaximize() {
        ipcRenderer.send('appMaximize')
      }
    },
    computed: {
      platform() {
        return this.$store.state.globalView.platform
      }
    }
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
    z-index: 2;
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
