<template lang="pug">
  v-chart.pc-chart_chart(
    :auto-resize="true"
    theme="quantum"
    :options="optionChart"
  )
</template>

<script>
  const xAxisMax = 14;
  export default {
    name: "ResourceMonitor",
    props: {
      monitorValueName: {
        type: String,
        default: ''
      },
      monitorValue: {
        type: Object,
      },
    },
    data() {
      return {
        requestsNum: 0,
        optionChart: {
          grid: { top: '10', bottom: '10', right: '10', left: '35' },
          dataZoom: [{ type: 'slider', show: false, realtime: true, startValue: 0, endValue: xAxisMax }],
          xAxis: {
            data: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14],
            axisLabel: { show: false }
          },
          yAxis: { type: 'value', min: 0, max: 100 },
          series: [{ type: 'line', data: [], symbolSize: 0 }]
        },
      }
    },
    watch: {
      monitorValue(newVal) {
        const curX = this.requestsNum;
        const lastX = curX + 2;
        if(curX > xAxisMax - 2) {
          this.optionChart.xAxis.data.push(lastX);
          this.optionChart.dataZoom[0].endValue = lastX;
          this.optionChart.dataZoom[0].startValue = lastX - xAxisMax;
        };
        this.optionChart.series[0].data.push(newVal[this.monitorValueName]);
        this.requestsNum++;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .pc-chart_chart {
    position: absolute !important;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
</style>
