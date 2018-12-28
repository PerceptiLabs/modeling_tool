<template lang="pug">
  header.app-header
    .app-header_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    nav.app-header_nav
      the-menu(:fullView="fullView")
    ul.app-header_actions
      button.btn.btn--app-minify(type="button" @click="appMinimize()").i.icon.icon-minus
      button.btn.btn--app-full(type="button" @click="appMaximize()").i.icon.icon-full-screen
      button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-close
</template>

<script>
  import {ipcRenderer} from 'electron'
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "TheHeader",
  components: {TheMenu},
  props: {
    fullView: { type: Boolean, default: true}
  },
  data() {
    return {

    }
  },
  methods: {
    appClose() {
      ipcRenderer.send('appClose')
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
  @import "../scss/base";
  .app-header {
    position: relative;
    z-index: 2;
    background: #141419;
    display: flex;
    align-items: center;
    height: $h-header;
    -webkit-app-region: drag;
    .btn {
      -webkit-app-region: no-drag;
    }
  }
  .app-header_logo {
    padding-left: 2rem;
    padding-right: 2rem;
    img {
      height: $h-header - 1;
    }
  }

  .app-header_actions {
    margin-left: auto;
    display: flex;
    .btn {
      height: $h-header;
      width: $h-header * 2;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5em;
      border-radius: 0;
      &:hover {
        background: $bg-grad-disable;
      }
    }
    .btn--app-minify {

    }
    .btn--app-full {

    }
    .btn--app-close {
      &:hover {
        background: $col-error;
      }
    }
  }
</style>
