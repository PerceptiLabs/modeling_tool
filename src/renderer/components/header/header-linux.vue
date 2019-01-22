<template lang="pug">
  .app-header
    .app-header_title
      .title_app-name PerceptiLabs
      ul.title_app-actions
        button.btn.btn--app-minify(type="button" @click="appMinimize()").i.icon.icon-appMinimaze
        button.btn.btn--app-full(type="button" @click="appMaximize()").i.icon.icon-appResize
        button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-appClose
    nav.app-header_nav
      the-menu
</template>

<script>
  import {ipcRenderer} from 'electron'
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "HeaderLinux",
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
    position: relative;
    z-index: 2;
    -webkit-app-region: drag;
    background: #272727;
    .btn {
      -webkit-app-region: no-drag;
    }
  }
  .app-header_title {
    height: $h-header;
    background: linear-gradient(180deg, #454545 0%, #212121 100%);
    display: flex;
    align-items: center;
  }
  .title_app-name {
    text-align: center;
    font-size: 1.4rem;
    font-weight: 700;
    flex-grow: 1;
  }

  .app-header_nav {
    height: 22px;
    -webkit-app-region: no-drag;
  }

  .title_app-actions {
    margin-left: auto;
    display: flex;
    .btn {
      height: 18px;
      width: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      background: linear-gradient(180deg, #8F8F8F 0%, #323233 100%);
      color: #1f1f24;
      font-weight: 900;
      font-size: 0.8rem;
      border-radius: 20rem;
      margin-right: 1rem;
      border: 1px solid #1e1e1e;
      &:hover {
        background: #545353;
      }
    }
    .btn--app-minify {

    }
    .btn--app-full {

    }
    .btn--app-close {
      background: linear-gradient(180deg, #F47979 0%, #E32727 100%);
      &:hover {
        background: #E94040;
      }
    }
  }
</style>
