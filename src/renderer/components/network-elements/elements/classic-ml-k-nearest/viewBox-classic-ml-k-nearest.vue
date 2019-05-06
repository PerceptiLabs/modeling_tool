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

  export default {
    name: "ViewClassicMLKNN",
    components: {ChartBase},
    data() {
      return {
        optionS: dataS,
        optionLine2: null,
        optionBar3: null,
        optionBar4: null,

      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
