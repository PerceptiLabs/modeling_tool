<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-switch(
        chartLabel="Data"
        :chartData="chartData.Data"
      )
</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDataData",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.boxElementID, 'DataData', '')
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
