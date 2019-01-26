<template lang="pug">
  .app-header
    .app-header_logo
      img(src="~@/assets/logo_small_dark.svg" alt="percepti labs logo")
    the-menu
    ul.app-header_actions
      button.btn.btn--app-minify(type="button" @click="appMinimize()").i.icon.icon-appMinimaze
      button.btn.btn--app-full(type="button" @click="appMaximize()").i.icon.icon-appResize
      button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-appClose
</template>

<script>
  import {ipcRenderer} from 'electron'
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "HeaderWin",
  components: {TheMenu},
  methods: {
    appClose() {
      this.$emit('appClosed')
    },
    appMinimize() {
      this.$emit('appMinimized')
    },
    appMaximize() {
      this.$emit('appMaximized')
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .app-header {
    display: flex;
    align-items: center;
    height: $h-header-win;
    background: #141419;
  }
  .app-header_logo {
    margin: 0 12px;
  }

  .app-header_actions {
    display: flex;
    margin-left: auto;
    .btn {
      font-size: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      width: $h-header-win * 2;
      height: $h-header-win;
      border-radius: 0;
      &:hover {
        background: #545353;
      }
    }
    .btn--app-close {
      &:hover {
        background: #e94040;
      }
    }
  }
</style>
