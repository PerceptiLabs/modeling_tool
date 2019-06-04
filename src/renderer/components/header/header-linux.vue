<template lang="pug">
  .app-header
    .app-header_title
      .title_app-name PerceptiLabs
      ul.title_app-actions
        button.btn.btn--app-minify(type="button" @click="appMinimize()").i.icon.icon-app-minimize
        button.btn.btn--app-full(type="button" @click="appMaximize()").i.icon.icon-app-resize
        button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-app-close
    the-menu.app-header_nav
</template>

<script>
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "HeaderLinux",
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
    background: #272727;
  }
  .app-header_title {
    display: flex;
    align-items: center;
    height: $h-header-linux - 22px;
    background: linear-gradient(180deg, #454545 0%, #212121 100%);
  }
  .title_app-name {
    font-size: 14px;
    font-weight: 700;
    flex-grow: 1;
    text-align: center;
  }

  .app-header_nav {
    height: 22px;
  }

  .title_app-actions {
    display: flex;
    margin-left: auto;
    .btn {
      font-size: 8px;
      font-weight: 900;
      color: #1f1f24;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 18px;
      height: 18px;
      margin-right: 7px;
      border: 1px solid #1e1e1e;
      border-radius: 50%;
      background: linear-gradient(180deg, #8f8f8f 0%, #323233 100%);
      &:hover {
        background: #545353;
      }
    }
    .btn--app-close {
      background: linear-gradient(180deg, #f47979 0%, #e32727 100%);
      &:hover {
        background: #e94040;
      }
    }
  }

</style>
