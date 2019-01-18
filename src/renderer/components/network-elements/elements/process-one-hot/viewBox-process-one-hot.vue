<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chartLabel="Output"
        :chartData="chartData.Output"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base.vue";
  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewProcessOneHot",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    methods: {
      getStatistics() {
        this.chartRequest(this.boxElementID, 'ProcessOneHot', '');
      },
      getData() {
        this.getStatistics()
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
