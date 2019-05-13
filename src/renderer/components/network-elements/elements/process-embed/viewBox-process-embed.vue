<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chart-label="Accuracy during one epoch"
        :chart-data="optionLine1"
      )
</template>

<script>
  import ChartBase from "@/components/charts/chart-base";

  export default {
    name: "ViewBoxProcessEmbed",
    components: {ChartBase},
    data() {
      return {
        optionLine1: null,
      }
    },
  }
</script>
