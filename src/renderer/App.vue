<template lang="pug">
  #app
    header-win
    //header-linux
    //header-mac
    router-view
</template>

<script>
  import {ipcRenderer}  from 'electron'
  import HeaderWin      from '@/components/header/header-win.vue'
  import HeaderMac      from '@/components/header/header-mac.vue'
  import HeaderLinux    from '@/components/header/header-linux.vue'

  export default {
    name: 'quantumnet',
    components: {HeaderWin, HeaderMac, HeaderLinux},
    mounted() {
      //main process events
      ipcRenderer.on('newNetwork', (event) => {
        this.$store.commit('mod_workspace/ADD_network');
      });
      ipcRenderer.on('openNetwork', (event) => {
        this.$store.commit('mod_events/set_openNetwork')
      });
      ipcRenderer.on('saveNetwork', (event) => {
        this.$store.commit('mod_events/set_saveNetwork')
      });
      ipcRenderer.on('closeApp', (event) => {
        this.$store.dispatch('mod_events/EVENT_closeCore');
      });
      ipcRenderer.on('info', (event, data) => {
        console.log(data);
      });
      ipcRenderer.send('appReady');
    },
  }
</script>

<style lang="sass">
  @import 'scss/common'
</style>
