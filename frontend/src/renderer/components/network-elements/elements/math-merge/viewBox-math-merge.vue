<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-switch(
        chart-label="Output"
        :chart-data="chartData.Output"
      )
</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxMathMerge",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    methods: {
      getData() {
        this.chartRequest(this.networkElement.layerId, 'MathMerge', '')
      }
    }
  }
</script>
