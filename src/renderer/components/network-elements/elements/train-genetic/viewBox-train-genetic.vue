<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-switch(
          :chart-data="optionBar"
        )
        chart-switch(
          chart-label="Reward during one epoch"
          :chart-data="optionLine1"
        )
</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch.vue";

  export default {
    name: "ViewBoxTrainGenetic",
    components: {ChartSwitch},
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
