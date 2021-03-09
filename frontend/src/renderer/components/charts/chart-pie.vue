<template lang="pug">
  v-chart(
    ref="chart"
    :auto-resize="true"
    :options="chartModel"
    theme="quantum"
  )
</template>

<script>
  import chartMixin       from "@/core/mixins/charts.js";

  export default {
    name: "ChartPie",
    mixins: [chartMixin],
    data() {
      return {
        defaultModel: {
          tooltip: {
            show: true,
            confine: true,
            backgroundColor: '#475D9C',
            textStyle: {
              fontSize: 10
            }
          },
          toolbox: {
            feature: {
              saveAsImage: {
                title: 'Save',
                show: false
              },
            }
          },
          series: []
        },
      }
    },
    methods: {
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


