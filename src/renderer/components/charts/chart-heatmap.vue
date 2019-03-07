<template lang="pug">
  .base-chart(
  ref="baseChart"
  :class="{'full-view': fullView}")
    .base-chart_head(v-if="!headerOff")
      .chart-head_title
        h5.ellipsis {{ chartLabel }}
      .chart-head_meta
        button.btn.btn--link(type="button"
        :class="{'text-primary': fullView}"
        @click="toggleFullView")
          i.icon.icon-full-screen-graph
    .base-chart_main
      v-chart(
      ref="chart"
      :auto-resize="true"
      theme="quantum"
      :options="chartModel"
      )
</template>

<script>
import {pathWebWorkers, chartSpinner} from '@/core/constants.js'
import chartMixin                     from "@/core/mixins/charts.js";

export default {
  name: "ChartHeatmap",
  mixins: [chartMixin],
  data() {
    return {
      chartSpinner,
      defaultModel: {
        tooltip: {},
        grid: {
          right: 50
        },
        xAxis: {
          boundaryGap: true,
          data: []
        },
        yAxis: {
          boundaryGap: true,
          data: []
        },
        visualMap: {
          min: 0,
          max: 1,
          top: '10px',
          itemHeight: 300,
          realtime: false,
          left: 'right',
        },
        series: []
      }
    }
  },
  methods: {
    createWWorker() {
      this.wWorker = new Worker(`${pathWebWorkers}/calcChartHeatMap.js`);
      this.wWorker.addEventListener('message', this.drawChart, false);
    },
    sendDataToWWorker(data) {
      if (data === null || data === undefined) {
        this.chartModel = this.defaultModel;
        return
      }
      let model = {...this.defaultModel};
      model.series = data[0];
      //model.series = dataHeat.series[0];

      this.wWorker.postMessage(model);
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
