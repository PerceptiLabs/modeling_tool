<template>
  <div id="app">
    <the-header></the-header>
    <router-view></router-view>
  </div>
</template>

<script>
  import {ipcRenderer} from 'electron'
  import TheHeader from '@/components/the-header.vue'

  export default {
    name: 'quantumnet',
    components: {TheHeader},
    mounted() {
      ipcRenderer.on('newNetwork', (event) => {
        //console.log(event);
        this.$store.commit('mod_workspace/ADD_loadNetwork');
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
