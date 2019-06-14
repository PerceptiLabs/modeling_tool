<template lang="pug">
  .base-chart(
    ref="baseChart"
    :class="{'full-view': fullView}"
    )
    .base-chart_head
      .chart-head_title
        h5.ellipsis {{ chartLabel }}
      .chart-head_meta
        button.btn.btn--link(type="button"
          :class="{'text-primary': fullView}"
          @click="toggleFullView"
        )
          i.icon.icon-full-screen-graph
    .base-chart_main
      request-spinner(:showSpinner="showRequestSpinner")
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
  import RequestSpinner from '@/components/different/request-spinner.vue'

  export default {
    name: "ChartBase",
    mixins: [chartMixin],
    components: {RequestSpinner},
    created() {
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
      applyCustomColor() {
        if (this.customColor.length) {
          this.defaultModel.color = this.customColor;
        }
      },
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
    watch: {

    }
  }
</script>