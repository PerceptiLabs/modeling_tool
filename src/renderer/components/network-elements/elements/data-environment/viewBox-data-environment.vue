<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-picture(
        chartLabel="Accuracy during one epoch"
        :chartData="chartData.Data"
      )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import ChartPicture    from "@/components/charts/chart-picture.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDataEnvironment",
    components: {ChartBase, ChartPicture},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.boxElementID, 'DataEnvironment', '')
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
