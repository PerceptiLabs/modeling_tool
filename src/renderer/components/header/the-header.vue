<template lang="pug">
  header.app-header

</template>
<script>
import {ipcRenderer}  from 'electron'
import HeaderLinux    from '@/components/header-linux.vue'
import HeaderWin      from '@/components/header-win.vue'
import HeaderMac      from '@/components/header-mac.vue'
  export default {
    name: 'TheHeader',
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
      header() {
        switch (process.platform) {
          case 'win32':
            
            break;
          case 'darwin':
            
            break;
          case 'linux':
            
            break;
        }
      }
    }
  }
</script>
<style>

</style>

