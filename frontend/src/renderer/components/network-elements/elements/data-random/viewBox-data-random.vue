<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-switch(
        chart-label="Input during one epoch"
        :chart-data="chartData.Data"
      )
</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDataRandom",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.networkElement.layerId, 'DataRandom', '')
      }
    }
  }
</script>
