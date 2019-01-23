<template lang="pug">
  .app-header
    ul.app-header_actions
      button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-appClose
      button.btn.btn--app-full(type="button" @click="appMinimize()").i.icon.icon-appMinimaze
      button.btn.btn--app-minify(type="button" @click="appMaximize()").i.icon.icon-appMacFullScreenOn
    .app-header_title PerceptiLabs
</template>

<script>
  import {ipcRenderer} from 'electron'
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "HeaderMac",
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
  $yellowBG: #f6c251;
  $redBG: #ff6157;
  $greenBG: #2acb42;

  .app-header {
    display: flex;
    align-items: center;
    height: $h-header-mac;
    background: linear-gradient(180deg, #4a4a4a 0%, #3e3e3e 100%);
  }
  .app-header_actions {
    display: flex;
    margin-left: auto;
    .btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 12px;
      height: 12px;
      margin-left: 10px;
      border-radius: 50%;
      font-size: 6px;
      font-weight: 900;
    }
    .btn--app-minify {
      background: $greenBG;
      color: $greenBG;
      font-size: 9px;
      border: 1px solid #24ad38;
      &:hover {
        color: #188228;
      }
    }
    .btn--app-full {
      background: $yellowBG;
      color: $yellowBG;
      border: 1px solid #d1a545;
      &:hover {
        color: #af811e;
      }
    }
    .btn--app-close {
      background: $redBG;
      color: $redBG;
      border: 1px solid #d9524a;
      &:hover {
        color: #941c15;
      }
    }
  }
  .app-header_title {
    font-size: 12px;
    flex-grow: 1;
    text-align: center;
  }


</style>
