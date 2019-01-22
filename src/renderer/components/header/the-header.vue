<template lang="pug">
  header
    header-win(
      v-if="operationSystem === 'win32'" 
      @appClosed='appClose'
      @appMinimized='appMinimize'
      @appMaximized='appMaximize'
    )
    header-mac(
      v-if="operationSystem === 'darwin'"
      @appClosed='appClose'
      @appMinimized='appMinimize'
      @appMaximized='appMaximize'
    )
    header-linux(
      v-if="operationSystem === 'linux'"
      @appClosed='appClose'
      @appMinimized='appMinimize'
      @appMaximized='appMaximize'
    )
</template>
<script>
import {ipcRenderer}  from 'electron'
import HeaderLinux    from '@/components/header/header-linux.vue'
import HeaderWin      from '@/components/header/header-win.vue'
import HeaderMac      from '@/components/header/header-mac.vue'
  export default {
    name: 'TheHeader',
    components: {
      HeaderLinux,
      HeaderWin,
      HeaderMac
    },
    data() {
      return {

      }
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
      operationSystem() {
        return process.platform
      }
    }
  }
</script>
<style>

</style>

