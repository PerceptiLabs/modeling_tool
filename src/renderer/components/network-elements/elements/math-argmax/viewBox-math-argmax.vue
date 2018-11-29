<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine1"
      )
</template>

<script>
  import ChartBase from "@/components/charts/chart-base";
  import dataLine  from "@/components/charts/line.js";
  export default {
    name: "ViewBoxMathArgmax",
    components: {ChartBase},
    data() {
      return {
        optionLine1: dataLine,
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
