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
    update-popup(
      :isShowPopup="updateShowPopup"
      @updateStarted="updateStart"
    )
</template>

<script>
  import uuid           from 'uuid/v4';
  import {ipcRenderer}  from 'electron'

  import {openLoadDialog, loadNetwork} from '@/core/helpers.js'

  import HeaderLinux    from '@/components/header/header-linux.vue';
  import HeaderWin      from '@/components/header/header-win.vue';
  import HeaderMac      from '@/components/header/header-mac.vue';
  import updatePopup    from '@/components/global-popups/update-popup/update-popup.vue'


  export default {
    name: 'quantumnet',
    components: { HeaderLinux, HeaderWin, HeaderMac, updatePopup },
    data() {
      return {
        updateShowPopup: false,
        userId: ''
      }
    },
    mounted() {
      this.checkToken();
      this.checkUserID();

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
        if(data.updateFounded) this.updateShowPopup = true;
        console.log('DATA', data);
      });
      ipcRenderer.on('getAppVersion', (event, data) => {
        this.$store.commit('globalView/SET_appVersion', data)
      });

      ipcRenderer.send('appReady', this.userId);
    },
    computed: {
      platform() {
        return this.$store.state.globalView.platform
      },
      eventLoadNetwork() {
        return this.$store.state.mod_events.openNetwork
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
        this.openLoadDialog(this.loadNetwork, opt)
      },
      '$route': {
        handler(to, from) {
          if(process.env.NODE_ENV === 'production') {
            ipcRenderer.send('changeRoute', to.fullPath)
          }
        },
        immediate: true
      }
    },
    methods: {
      openLoadDialog,
      loadNetwork,
      appClose() {
        this.$store.dispatch('mod_events/EVENT_closeCore');
      },
      appMinimize() {
        ipcRenderer.send('appMinimize')
      },
      appMaximize() {
        ipcRenderer.send('appMaximize')
      },
      updateStart() {
        console.log('From App');
        ipcRenderer.send('update-start')
      },
      checkUserID() {
        let localUserID = localStorage.getItem('userId');
        if(localUserID) {
          this.userId = localUserID;
        }
        else {
          this.userId = uuid();
          localStorage.setItem('userId', this.userId)
        }
        this.$store.commit('globalView/SET_userID', this.userId);
      },
      checkToken() {
        let localUserToken = localStorage.getItem('userToken');
        if(localUserToken) {
          this.$store.commit('globalView/SET_userToken', localUserToken);
        }
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
