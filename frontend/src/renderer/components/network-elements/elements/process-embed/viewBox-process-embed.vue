<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-switch(
        chart-label="Accuracy during one epoch"
        :chart-data="optionLine1"
      )
</template>

<script>
  import ChartSwitch from "@/components/charts/chart-switch";

  export default {
    name: "ViewBoxProcessEmbed",
    components: {ChartSwitch},
    data() {
      return {
        optionLine1: null,
      }
    },
  }
</script>
