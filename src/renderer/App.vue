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
      ipcRenderer.on('openUntrain', (event) => {
        this.$store.dispatch('mod_events/EVENT_openFile')
      })
    },
  }
</script>

<style lang="sass">
  @import 'scss/common'
</style>
