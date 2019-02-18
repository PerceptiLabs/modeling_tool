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
          @click="toggleFullView"
        )
          i.icon.icon-full-screen-graph
    .base-chart_main
      v-chart(
        ref="chart"
        :auto-resize="true"
        :options="chartModel"
        theme="quantum"
      )
</template>

<script>
  import {pathWebWorkers, chartSpinner} from '@/core/constants.js'

  export default {
    name: "ChartBase",
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
        type: Object,
        default: function () {
          return null
        }
      },
      customColor: {
        type: Array,
        default: function () {
          return []
        }
      },
    },
    mounted() {
      this.applyCustomColor();
      this.createWWorker();
      this.$refs.chart.showLoading(chartSpinner)
    },
    beforeDestroy() {
      this.wWorker.postMessage('close');
      this.wWorker.removeEventListener('message', this.drawChart, false);
      this.$refs.chart.dispose();
    },
    data() {
      return {
        fullView: false,
        wWorker: null,
        chartModel: {},
        defaultModel: {
          tooltip: {},
          toolbox: {
            feature: {
              saveAsImage: {
                title: 'Save'
              },
              //magicType: {type: ['line', 'bar']},
            }
          },
          legend: {},
          yAxis: {},
          xAxis: {
            //boundaryGap: true,
            data: []
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
        let model = {...this.defaultModel, ...this.chartData};
        model.xAxis.data.length = 0;
        this.wWorker.postMessage({
          model,
          xLength: this.chartData.xLength
        });
      }
    },
    methods: {
      toggleFullView() {
        this.fullView = !this.fullView;
        this.$nextTick(()=>this.$refs.chart.resize());
      },
      applyCustomColor() {
        if (this.customColor.length) {
          this.defaultModel.color = this.customColor;
        }
      },
      createWWorker() {
        this.wWorker = new Worker(`${pathWebWorkers}/calcChartBase.js`);
        this.wWorker.addEventListener('message', this.drawChart, false);
      },
      drawChart(ev) {
        this.chartModel = ev.data;
        this.$refs.chart.hideLoading()
      }
    },
  }
</script>

<style lang="scss" scoped>
  .base-chart_main {
    height: 300px;
  }
</style>
