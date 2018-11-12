<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionS"
        )
        chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionBar3"
        )
      .statistics-box_row
        chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine2"
        )
        chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionBar4"
        )
</template>

<script>
  import ChartLine    from "@/components/charts/chart-line";
  import ChartBar     from "@/components/charts/chart-bar";
  import ChartScatter from "@/components/charts/chart-scatter";

  import dataLine  from "@/components/charts/line.js";
  import dataBar  from "@/components/charts/bar.js";
  import dataS  from "@/components/charts/scatter.js";
  export default {
    name: "ViewBoxLearnClassKMeans",
    components: {ChartLine, ChartBar, ChartScatter},
    data() {
      return {
        optionS: dataS,
        optionLine2: dataLine,
        optionBar3: dataBar,
        optionBar4: dataBar,

      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
