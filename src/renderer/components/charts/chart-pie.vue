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
      .base-chart_info(v-if="chartInfo.length") {{ chartInfo }}
</template>

<script>
  import {pathWebWorkers, chartSpinner} from '@/core/constants.js'
  import chartMixin                     from "@/core/mixins/charts.js";

  export default {
    name: "ChartPie",
    mixins: [chartMixin],
    mounted() {
      this.applyCustomColor();
    },
    data() {
      return {
        chartSpinner,
        defaultModel: {
          toolbox: {
            feature: {
              saveAsImage: {
                title: 'Save'
              },
            }
          },
          series: []
        },
      }
    },
    computed: {
      chartInfo() {
        if(this.chartModel.series && this.chartModel.series.length && typeof this.chartModel.series[0].data[0].value === 'number') {
          const info = this.chartModel.series[0].data[0].value.toFixed(2);
          return `${info}%`
        }
        return ''
      }
    },
    methods: {
      applyCustomColor() {
        if (this.customColor.length) {
          this.defaultModel.color = this.customColor;
        }
      },
      createWWorker() {

      },
      sendDataToWWorker(dataWatch) {
        let data = dataWatch || this.chartData;
        if (!data) {
          this.chartModel = this.defaultModel;
          return
        }
        let model = {...this.defaultModel, ...data};
        let currentData = model.series[0];
        let addOptions = {
          label: {
            normal: { show: false },
            emphasis: { show: false }
          },
          lableLine: {
            normal: { show: false },
            emphasis: { show: false }
          },
        };
        model.series[0] = {...currentData, ...addOptions};
        this.drawChart({data: model});

      }
    },
  }
</script>

<style lang="scss" scoped>
  .base-chart_main {
    height: 200px;
  }
  .base-chart_info {
    font-size: 2rem;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    .full-view & {
      z-index: 3;
    }
  }
</style>
