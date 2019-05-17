<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chart-label="Data"
        :chart-data="chartData.Output"
      )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxMathMerge",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.boxElementID, 'MathMerge', '')
      }
    }
  }
</script>
