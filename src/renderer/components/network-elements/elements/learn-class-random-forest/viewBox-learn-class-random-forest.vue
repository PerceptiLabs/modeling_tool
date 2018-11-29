<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="optionS"
        )
        chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="optionBar3"
        )
      .statistics-box_row
        chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine2"
        )
        chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="optionBar4"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base.vue";

  import dataLine  from "@/components/charts/line.js";
  import dataBar  from "@/components/charts/bar.js";
  import dataS  from "@/components/charts/scatter.js";
  export default {
    name: "ViewBoxLearnClassRandomForest",
    components: {ChartBase},
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
