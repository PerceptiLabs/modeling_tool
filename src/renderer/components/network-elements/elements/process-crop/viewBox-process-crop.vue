<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-switch(
        chart-label="Output"
        :chart-data="chartData.ProcessCrop"
      )

</template>

<script>
  import ChartSwitch from "@/components/charts/chart-switch";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxProcessCrop",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.boxElementID, 'ProcessCrop', '')
      }
    },
  }
</script>
