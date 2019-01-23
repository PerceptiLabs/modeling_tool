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
import dataHeat     from "@/components/charts/hear.js";
export default {
  name: "ChartHeatmap",
  props: {
    headerOff: {
      type: Boolean,
      default: false
    },
    chartLabel: {
      type: String,
      default: ''
    },
    chartData: {
      type: Array,
      default: function() {
        return null
      }
    },
  },
  data() {
    return {
      fullView: false,
      chartModel: {},
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
  watch: {
    chartData() {
      if (this.chartData === null) {
        this.chartModel = this.defaultModel;
        return
      }
      let model = {...this.defaultModel};
      model.series = this.chartData[0];
      //model.series = dataHeat.series[0];

      this.wWorker.postMessage(model);
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    },
    createWWorker() {
      this.wWorker = new Worker(`${pathWebWorkers}/calcChartHeatMap.js`);
      this.wWorker.addEventListener('message', this.drawChart, false);
    },
    drawChart(ev) {
      this.chartModel = ev.data;
      this.$refs.chart.hideLoading()
    }
  },
  mounted() {
    this.createWWorker();
    this.$refs.chart.showLoading(chartSpinner)
  },
  beforeDestroy() {
    this.wWorker.postMessage('close');
    this.wWorker.removeEventListener('message', this.drawChart, false);
    this.$refs.chart.dispose();
  }
}
</script>

<style lang="scss" scoped>

</style>
