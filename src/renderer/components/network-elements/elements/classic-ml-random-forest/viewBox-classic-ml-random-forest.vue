<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-base(
          chart-label="Accuracy during one epoch"
        :chart-data="optionS"
        )
        chart-base(
          chart-label="Accuracy during one epoch"
        :chart-data="optionBar3"
        )
      .statistics-box_row
        chart-base(
          chart-label="Accuracy during one epoch"
        :chart-data="optionLine2"
        )
        chart-base(
          chart-label="Accuracy during one epoch"
        :chart-data="optionBar4"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base.vue";

  export default {
    name: "ViewClassicMLRandomForest",
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
