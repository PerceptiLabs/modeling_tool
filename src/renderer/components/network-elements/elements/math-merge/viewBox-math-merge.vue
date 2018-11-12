<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine1"
      )
</template>

<script>
  import ChartLine from "@/components/charts/chart-line";
  import dataLine  from "@/components/charts/line.js";
  export default {
    name: "ViewBoxMathMerge",
    components: {ChartLine},
    data() {
      return {
        optionLine1: dataLine,
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
