<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chartLabel="Data"
        :chartData="chartData.Data"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import dataLine     from "@/components/charts/line.js";
  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDataData",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    data() {
      return {
      }
    },
    computed: {

    },
    methods: {
      getStatistics() {
        this.chartRequest(this.boxElementID, 'DataData', '')
      },
    }
  }
</script>

<style lang="scss" scoped>

</style>
