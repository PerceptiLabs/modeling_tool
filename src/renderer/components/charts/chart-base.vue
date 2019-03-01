<template lang="pug">
  .base-chart(
    ref="baseChart"
    :class="{'full-view': fullView}"
    )
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
  import chartMixin                     from "@/core/mixins/charts.js";

  export default {
    name: "ChartBase",
    mixins: [chartMixin],
    mounted() {
      this.applyCustomColor();
    },
    data() {
      return {
        chartSpinner,
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
      applyCustomColor() {
        if (this.customColor.length) {
          this.defaultModel.color = this.customColor;
        }
      },
      createWWorker() {
        this.wWorker = new Worker(`${pathWebWorkers}/calcChartBase.js`);
        this.wWorker.addEventListener('message', this.drawChart, false);
      }
    },
  }
</script>

<style lang="scss" scoped>
  .base-chart_main {
    height: 300px;
  }
</style>
