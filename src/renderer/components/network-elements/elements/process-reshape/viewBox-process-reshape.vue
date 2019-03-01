<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-picture(
        chartLabel="Output"
        :chartData="chartData.Output"
        )
</template>

<script>
  import ChartPicture    from "@/components/charts/chart-picture.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxProcessReshape",
    components: {ChartPicture},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.boxElementID, 'ProcessReshape', '')
      }
    }
  }
</script>
