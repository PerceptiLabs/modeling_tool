<template lang="pug">
  section.sidebar-content
    //.chart-box
      span.chart_title.big-text Progressbar
      .chart_main.graf
    .chart-box
      span.chart_title.big-text RAM
      .chart_main.graf
        v-chart(
          :options="optionRAM"
          :init-options="initOptions"
          )
    //.chart-box
      span.chart_title.big-text CPU
      .chart_main.graf
    //.chart-box
      span.chart_title.big-text GPU
      .chart_main.graf

</template>

<script>
  import 'echarts/lib/chart/line'
  import 'echarts/lib/component/polar'
export default {
  name: "SidebarTraining",
  data() {
    return {
      initOptions: {
        renderer: 'svg',
      },
      optionRAM: {
        grid: {
          top: '10',
          bottom: '25',
          right: '10',
          left: '35',
        },
        textStyle: {
          color: '#e1e1e1',
        },
        singleAxis: {axisLine: {lineStyle: {color: '#F00'}}},
        parallel: {parallelAxisDefault: {axisLine: {lineStyle: {color: '#F00'}}}},
        parallelAxis: {
          areaSelectStyle: {
            color: '#F0f',
            opacity: 1
          }
        },




        xAxis: {
          type: 'category',
          data: [1, 2, 3, 4, 5, 6, 7],
          axisLine: {lineStyle: {color: '#3C3C4C'}},
          nameTextStyle: {fontSize: 10}
      },
        yAxis: {
          type: 'value',
          axisLine: {lineStyle: {color: '#3C3C4C'}},
          nameTextStyle: {fontSize: 10}
        },
        series: [{
          data: [82, 93, 90, 93, 12, 13, 13],
          type: 'line',
          smooth: true
        }]
      }
    }
  },
  methods: {

  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar-content {
    padding-top: 1rem;
  }
  .graf {
    //height: 87px;
    height: 400px;
    background-color: $bg-workspace;
  }
</style>
