<template lang="pug">
  #app
    the-header
    router-view
</template>

<script>
  import {ipcRenderer} from 'electron'
  import TheHeader from '@/components/the-header.vue'

  export default {
    name: 'quantumnet',
    components: {TheHeader},
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
