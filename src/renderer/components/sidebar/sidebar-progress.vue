<template lang="pug">
  .sidebar-progress
    .sidebar-progress_loader
    span.sidebar-progress_data.middle-text {{ percentData }}
</template>

<script>
export default {
  name: "SidebarProgress",
  props: {
    percent: [Number]
  },
  data() {
    return {

    }
  },
  computed: {
    percentData() {
      let result;
      this.percent ?  result = this.percent + '%' : result = '';
      return result
    }
  },
  methods: {

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
    margin: 0 auto;
    width: 8em;
    height: 8em;
    border-radius: 50%;
    background: $color-6;
    background: linear-gradient(to bottom, $color-6 25%, $bg-window 80%);
    animation: loader 1s infinite linear;
    transform: translate(0);
    overflow: hidden;
    &:before {
      content: '';
      position: absolute;
      top: 0;
      left: 50%;
      bottom: 0;
      width: 50%;
      background: $bg-window;

    }
    &:after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      bottom: 0;
      right: 0;
      background: $bg-workspace;
      width: 4.5em;
      height: 4.5em;
      border-radius: 50%;

      margin: auto;

    }
  }

  @keyframes loader {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
  .sidebar-progress_data {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
  }
</style>
