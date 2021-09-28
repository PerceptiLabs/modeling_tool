<template lang="pug">
  v-chart.pc-chart_chart(
    :auto-resize="true"
    :theme="theme"
    :options="optionChart"
  )
</template>

<script>
  import { mapState } from 'vuex';
  import { THEME_DARK } from '@/core/constants.js';

  const xAxisMax = 8;
  export default {
    name: "ResourceMonitor",
    props: {
      monitorValueKey: {
        type: String,
        default: ''
      },
      monitorValue: {
        type: Object,
      },
    },
    computed: {
      ...mapState({
        theme:                      state => state.globalView.theme
      }),
    },
    data() {
      return {
        requestsNum: 0,
        optionChart: {
          color: ['#FE7373', '#F7D081', '#73FEBB'],
          grid: { top: '10', bottom: '10', right: '10', left: '35' },
          dataZoom: [{ type: 'slider', show: false, realtime: true, startValue: 0, endValue: xAxisMax }],
          xAxis: {
            data: [0,1,2,3,4,5,6,7,8],
            axisLabel: { show: false },
          },
          yAxis: { type: 'value', min: 0, max: 100 },
          series: [{ type: 'line', data: [], symbolSize: 0 },
                   { type: 'line', data: [], symbolSize: 0 },
                   { type: 'line', data: [], symbolSize: 0 }
          
          ]
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
        const nextVal1 = newVal['Memory'] || 0;
        const nextVal2 = newVal['CPU'] || 0;
        const nextVal3 = newVal['GPU'] || 0;

        this.optionChart.series[0].data.push(nextVal1);
        this.optionChart.series[1].data.push(nextVal2);
        this.optionChart.series[2].data.push(nextVal3);

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
