<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-switch(
        chart-label="Data"
        :chart-data="chartData.Data"
      )
</template>

<script>
  import ChartSwitch      from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";
  import { mapActions } from 'vuex';

  export default {
    name: "ViewBoxIoOutput",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.boxElementID, 'IoOutput', '')
      }
    }
  }
</script>
