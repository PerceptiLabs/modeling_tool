<template lang="pug">
  header.app-header
    .app-header_logo
      a(@click="toProjectPage")
        img(src="./../../../../static/img/perceptilabs-logo-header.svg" alt="PerceptiLabs logo")
    the-menu

    ul.app-header_actions
      button.btn.btn--app-minify(type="button" @click="appMinimize()").i.icon.icon-app-minimize
      button.btn.btn--app-full(type="button"
        @click="appMaximize"
        :class="{'icon-app-restore-down': showRestoreIcon, 'icon-app-resize': !showRestoreIcon}").i.icon
      button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-app-close
</template>

<script>
  import TheMenu from '@/components/the-menu.vue'

export default {
  name: "HeaderWin",
  components: {TheMenu},
  computed: {
    showRestoreIcon() {
      return this.$store.state.globalView.appIsFullView
    }
  },
  methods: {
    appClose() {
      this.$emit('app-closed')
    },
    appMinimize() {
      this.$emit('app-minimized')
    },
    appMaximize() {
      this.$emit('app-maximized')
    },
    toProjectPage() {
      if(this.$route.name === 'app') {
        this.$router.push({name: 'projects'})
      }
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
    cursor: pointer;
    a {
      display: block;
      -webkit-app-region: no-drag;
    }
  }

  .app-header_actions {
    display: flex;
    margin-left: auto;
    .btn {
      font-size: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 46px;
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
