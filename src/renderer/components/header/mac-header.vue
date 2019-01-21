<template lang="pug">
  header.app-header
    ul.app-header_actions
      button.btn.btn--app-close(type="button" @click="appClose()")
      button.btn.btn--app-full(type="button" @click="appMaximize()")
      button.btn.btn--app-minify(type="button" @click="appMinimize()")
    .app-header_title PerceptiLabs
</template>

<script>
  import {ipcRenderer} from 'electron'
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "MacHeader",
  components: {TheMenu},
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
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .app-header {
    position: relative;
    z-index: 2;
    background: linear-gradient(180deg, #4A4A4A 0%, #3E3E3E 100%);
    display: flex;
    align-items: center;
    height: 2.1rem;
    -webkit-app-region: drag;
    .btn {
      -webkit-app-region: no-drag;
    }
  }
  .app-header_actions {
    margin-left: auto;
    display: flex;
    .btn {
      height: 1rem;
      width: 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 20rem;
      margin-left: 1rem;
      &:hover {
        background: #545353;
      }
    }
    .btn--app-minify {
      background: #2acb42;
      &:hover {
        background: #24af39;
      }
    }
    .btn--app-full {
      background: #d2d2d2;
      &:hover {
        background: #b1b1b1;
      }
    }
    .btn--app-close {
      background: #FF6157;
      &:hover {
        background: #E94040;
      }
    }
  }
  .app-header_title {
    flex-grow: 1;
    text-align: center;
    font-size: 1.2rem;
  }

</style>
