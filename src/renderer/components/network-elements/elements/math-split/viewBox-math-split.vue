<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chart-label="Output"
        :chart-data="optionLine1"
      )
</template>

<script>
  import ChartBase from "@/components/charts/chart-base";

  export default {
    name: "ViewBoxMathSplit",
    components: {ChartBase},
    data() {
      return {
        optionLine1: null,
      }
    },
  }
</script>
