<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-bar(
        :chartData="optionBar"
        )
        chart-line(
        chartLabel="Reward during one epoch"
        :chartData="optionLine1"
        )
</template>

<script>
  import ChartLine    from "@/components/charts/chart-lineBar";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";
  import data3d       from "@/components/charts/3d.js";
  import dataHeat     from "@/components/charts/hear.js";
  import dataBar      from "@/components/charts/bar.js";
  import dataLine     from "@/components/charts/line.js";

  export default {
    name: "ViewBoxTrainGenetic",
    components: {ChartLine, ChartHeatmap, ChartD3},
    data() {
      return {
        optionLine1: dataLine,
        option3d: data3d,
        optionHeat: dataHeat,
        optionBar: dataBar,
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
