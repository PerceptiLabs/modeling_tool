<template lang="pug">
  .pc-chart_box
    span.pc-chart_title.big-text {{sectionName}}
    .pc-chart_main
      slot

</template>

<script>

export default {
  name: "SidebarTrainingSection",
  props: {
    sectionName: {
      type: String,
      default: ''
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";

  .pc-chart_box {
    flex: 0 0 100%;
    width: 100%;
  }
  .pc-chart_title {
    display: block;
    margin: 1rem 0 .5rem;
  }
  .pc-chart_main {
    position: relative;
    height: 9rem;
    background-color: $bg-workspace;
  }
</style>
