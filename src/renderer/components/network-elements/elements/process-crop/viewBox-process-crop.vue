<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-heatmap(
        v-if="true"
        chartLabel="Output"
        :chartData="chartData.ProcessCrop"
      )
      chart-picture(
        v-else
        chartLabel="Output"
        :chartData="chartData.ProcessCrop"
      )

</template>

<script>
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartPicture from "@/components/charts/chart-picture.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxProcessCrop",
    components: {ChartHeatmap, ChartPicture},
    mixins: [viewBoxMixin],
    methods: {
      getStatistics() {
        this.chartRequest(this.boxElementID, 'ProcessCrop', '')
      },
    },
  }
</script>

<style lang="scss" scoped>

</style>
