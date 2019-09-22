<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      .statistics-box_row
        chart-switch(
          key="1"
          chart-label="Accuracy during one epoch"
          :chartData="optionS"
        )
        chart-switch(
          key="2"
          chart-label="Accuracy during one epoch"
          :chartData="optionBar3"
        )
      .statistics-box_row
        chart-switch(
          key="3"
          chart-label="Accuracy during one epoch"
          :chartData="optionLine2"
        )
        chart-switch(
          key="4"
          chart-label="Accuracy during one epoch"
          :chartData="optionBar4"
        )
</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch.vue";

  export default {
    name: "ViewClassicMLSVM",
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
