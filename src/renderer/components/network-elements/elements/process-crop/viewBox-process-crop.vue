<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-heatmap(
        v-if="true"
        chart-label="Output"
        :chart-data="chartData.ProcessCrop"
      )
      chart-picture(
        v-else
        chart-label="Output"
        :chart-data="chartData.ProcessCrop"
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
      getData() {
        this.chartRequest(this.boxElementID, 'ProcessCrop', '')
      }
    },
  }
</script>
