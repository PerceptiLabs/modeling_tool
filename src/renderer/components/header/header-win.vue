<template lang="pug">
  .app-header
    .app-header_logo
      router-link(:to="{name: 'projects'}")
        img(src="./../../../../static/img/logo_small_dark.svg" alt="percepti labs logo")
    the-menu
    ul.app-header_actions
      button.btn.btn--app-minify(type="button" @click="appMinimize()").i.icon.icon-app-minimize
      button.btn.btn--app-full(type="button" @click="appMaximize()").i.icon.icon-app-resize
      button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-app-close
</template>

<script>
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "HeaderWin",
  components: {TheMenu},
  methods: {
    appClose() {
      this.$emit('app-closed')
    },
    appMinimize() {
      this.$emit('app-minimized')
    },
    appMaximize() {
      this.$emit('app-maximized')
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
    background: #272727;
    font-family: sans-serif;
  }
  .app-header_logo {
    margin: 0 12px;
    a {
      display: block;
      -webkit-app-region: no-drag;
    }
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
