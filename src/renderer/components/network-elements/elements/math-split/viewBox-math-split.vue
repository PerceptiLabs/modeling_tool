<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-switch(
        chart-label="Output"
        :chart-data="optionLine1"
      )
</template>

<script>
  import ChartSwitch from "@/components/charts/chart-switch";

  export default {
    name: "ViewBoxMathSplit",
    components: {ChartSwitch},
    data() {
      return {
        optionLine1: null,
      }
    },
  }
</script>
