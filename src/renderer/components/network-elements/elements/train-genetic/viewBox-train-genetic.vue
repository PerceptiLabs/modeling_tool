<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-base(
        :chartData="optionBar"
        )
        chart-base(
        chartLabel="Reward during one epoch"
        :chartData="optionLine1"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base.vue";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";

  export default {
    name: "ViewBoxTrainGenetic",
    components: {ChartBase, ChartHeatmap, ChartD3},
    data() {
      return {
        optionLine1: null,
        option3d: null,
        optionHeat: null,
        optionBar: null,
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
