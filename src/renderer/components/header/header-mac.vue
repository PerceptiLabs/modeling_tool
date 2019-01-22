<template lang="pug">
  .app-header
    ul.app-header_actions
      button.btn.btn--app-close(type="button" @click="appClose()")
      button.btn.btn--app-full(type="button" @click="appMinimize()")
      button.btn.btn--app-minify(type="button" @click="appMaximize()")
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
      width: 10px;
      height: 10px;
      margin-left: 10px;
      border-radius: 50%;
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
      background: #f6c251;
      &:hover {
        background: #d4a642;
      }
    }
    .btn--app-close {
      background: #ff6157;
      &:hover {
        background: #e94040;
      }
    }
  }
  .app-header_title {
    font-size: 12px;
    flex-grow: 1;
    text-align: center;
  }


</style>
