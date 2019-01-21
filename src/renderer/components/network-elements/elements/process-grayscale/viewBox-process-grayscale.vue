<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-picture(
        chartLabel="Output"
        :chartData="chartData.Output"
      )
</template>

<script>
  import ChartPicture from "@/components/charts/chart-picture.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxProcessGrayscale",
    components: {ChartPicture},
    mixins: [viewBoxMixin],
    methods: {
      getStatistics() {
        this.chartRequest(this.boxElementID, 'ProcessGrayscale', '')
      },
      getData() {
        this.getStatistics()
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
