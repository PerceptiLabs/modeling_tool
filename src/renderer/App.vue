<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
  import {ipcRenderer} from 'electron'

  export default {
    name: 'quantumnet',
    mounted() {
      ipcRenderer.on('closeApp', (event, data) => {
        console.log(data);
        this.$store.dispatch('mod_api/API_CLOSE_core');
        setTimeout(()=>{
          ipcRenderer.send('acceptClose')
        }, 5000);
      });
      ipcRenderer.on('newNetwork', (event) => {
        console.log(event);
        this.$store.commit('mod_workspace/ADD_loadNetwork');
      });
      ipcRenderer.on('openNetwork', (event) => {
        this.$store.commit('mod_events/set_openNetwork')
      });
      ipcRenderer.on('saveNetwork', (event) => {
        this.$store.commit('mod_events/set_saveNetwork')
      })
    },
  }
</script>

<style lang="sass">
  @import 'scss/common'
</style>
