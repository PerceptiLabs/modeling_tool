<template lang="pug">
  .sidebar-progress
    .sidebar-progress_loader.animation-loader(:class="styleLoader")
    span.sidebar-progress_data.middle-text {{ percentData }}
</template>

<script>
export default {
  name: "SidebarProgress",
  data() {
    return {
      percentData: '0%',
      buffer: '0%'
    }
  },
  computed: {
    statusNetworkInfo() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus
    },
    statusNetworkCore() {
      return this.$store.getters['mod_workspace/GET_networkCoreStatus']
    },
    styleLoader() {
      return {
        'animation--paused': this.statusNetworkCore === 'Paused',
        'validation-style': this.statusNetworkCore === 'Validation'
      }
    },
    doShowCharts() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.chartsRequest.showCharts
    },
    isNeedWait() {
      return this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent']
    },
  },
  watch: {
    statusNetworkInfo(newVal) {
      let settings = newVal;
      let progress;
      if(settings === null) {
        progress = 0;
      }
      else progress = settings.Progress;
      let result = Math.round(progress * 100) + '%';
      //console.log(result);
      this.isNeedWait
        ? this.buffer = result
        : this.percentData = result
    },
    doShowCharts() {
      this.isNeedWait
        ? this.percentData = this.buffer
        : null
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar-progress {
    position: relative;
    padding: .5em;
  }
  .sidebar-progress_loader {
    display: block;
    overflow: hidden;
    width: 8em;
    height: 8em;
    margin: 0 auto;
    transform: translate(0);
    border-radius: 50%;
    background: linear-gradient(to bottom, $color-6 25%, $bg-window 80%);
    &.validation-style {
      background: linear-gradient(to bottom, #9173FF 25%, $bg-window 80%);
    }
    &:before {
      content: '';
      position: absolute;
      top: 0;
      bottom: 0;
      left: 50%;
      width: 50%;
      background: $bg-window;
    }
    &:after {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      width: 4.5em;
      height: 4.5em;
      margin: auto;
      border-radius: 50%;
      background: $bg-workspace;
    }
  }
  .sidebar-progress_data {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
</style>
