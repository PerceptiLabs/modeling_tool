<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-switch(
          key="1"
          chart-label="Accuracy during one epoch"
          :chart-data="optionS"
        )
        chart-switch(
          key="2"
          chart-label="Accuracy during one epoch"
          :chart-data="optionBar3"
        )
      .statistics-box_row
        chart-switch(
          key="3"
          chart-label="Accuracy during one epoch"
          :chart-data="optionLine2"
        )
        chart-switch(
          key="4"
          chart-label="Accuracy during one epoch"
          :chart-data="optionBar4"
        )
</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch.vue";

  export default {
    name: "ViewClassicMLKNN",
    components: {ChartSwitch},
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