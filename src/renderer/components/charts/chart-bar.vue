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
  name: "ChartBar",
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

</style>
