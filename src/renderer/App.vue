<template lang="pug">
  #app
    win-header
    //linux-header
    //mac-header
    router-view
</template>

<script>
  import {ipcRenderer}  from 'electron'
  import WinHeader      from '@/components/the-header.vue'
  import MacHeader      from '@/components/header/mac-header.vue'
  import LinuxHeader    from '@/components/header/linux-header.vue'

  export default {
    name: 'quantumnet',
    components: {WinHeader, MacHeader, LinuxHeader},
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
