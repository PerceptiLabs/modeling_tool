<template lang="pug">
  #app
    the-header(:fullView="menuSet")
    router-view
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
    data() {
      return {
        menuSet: false
      }
    },
    watch: {
      '$route' (to, from) {
        console.log('to', to);
        to.name === 'app' ? this.menuSet = true : this.menuSet = false
      }
    }
  }
</script>

<style lang="sass">
  @import 'scss/common'
</style>
