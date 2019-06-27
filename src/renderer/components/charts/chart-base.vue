<template lang="pug">
  v-chart(
    ref="chart"
    :auto-resize="true"
    :options="chartModel"
    theme="quantum"
  )
</template>

<script>
  import {pathWebWorkers}     from '@/core/constants.js'
  import chartMixin           from "@/core/mixins/charts.js";

  export default {
    name: "ChartBase",
    mixins: [chartMixin],
    data() {
      return {
        defaultModel: {
          tooltip: {},
          toolbox: {
            feature: {
              saveAsImage: {
                title: 'Save'
              },
            }
          },
          xAxis: { data: [] },
          yAxis: {},
          legend: {},
          series: []
        }
      }
    },
    methods: {
      createWWorker() {
        this.wWorker = new Worker(`${pathWebWorkers}/calcChartBase.js`);
        this.wWorker.addEventListener('message', this.drawChart, false);
      },
      sendDataToWWorker(dataWatch) {
        let data = dataWatch || this.chartData;
        if (data === null || data === undefined) {
          this.chartModel = this.defaultModel;
          return
        }
        let model = {...this.defaultModel, ...data};
        let typeChart = model.series[0].type;
        if(typeChart === 'bar') model.xAxis.boundaryGap = true;
        this.wWorker.postMessage({
          model,
          xLength: data.xLength
        });
      }
    },
  }
</script>