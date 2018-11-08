<template lang="pug">
  .base-chart(:class="{'full-view': fullView}")
    .base-chart_head
      .chart-head_title
        h5 {{ chartLabel }}
      .chart-head_meta
        button.btn.btn--link(type="button"
          @click="toggleFullView")
          i.icon.icon-full-screen-graph
    .base-chart_main
      v-chart(
        :auto-resize="true"
        theme="quantum"
        :options="chartData"
      )
</template>

<script>

export default {
  name: "ChartLine",
  props: {
    chartLabel: {
      type: String,
      default: ''
    },
    chartData: {
      type: Object,
      default: function() {
        return {}
      }
    },
  },
  data() {
    return {
      fullView: false
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    }
  }
}
</script>

<style lang="scss" scoped>
  .full-view {
    position: absolute;
    z-index: 1;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
  }
</style>
