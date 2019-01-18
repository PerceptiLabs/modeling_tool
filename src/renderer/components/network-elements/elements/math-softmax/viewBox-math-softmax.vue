<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="chartData.Output"
      )
</template>

<script>
  import ChartBase from "@/components/charts/chart-base";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxMathSoftmax",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    methods: {
      getStatistics() {
        this.chartRequest(this.boxElementID, 'MathSoftmax', '')
      },
    },
  }
</script>

<style lang="scss" scoped>

</style>
