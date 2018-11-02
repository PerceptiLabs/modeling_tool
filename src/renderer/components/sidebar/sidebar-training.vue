<template lang="pug">
  section.sidebar-content
    .chart-box
      span.chart_title.big-text Progressbar
      .chart_main.graf
        sidebar-progress(:percent="progress")
    .chart-box
      span.chart_title.big-text RAM
      .chart_main.graf
        chart-line(:chartData="optionRAM")
    .chart-box
      span.chart_title.big-text CPU
      .chart_main.graf
        chart-line(:chartData="optionCPU")
    .chart-box
      span.chart_title.big-text GPU
      .chart_main.graf
        chart-line(:chartData="optionGPU")

</template>

<script>
import SidebarProgress from "./sidebar-progress";
import ChartLine from "../charts/chart-line";

export default {
  name: "SidebarTraining",
  components: {ChartLine, SidebarProgress},
  mounted() {
    this.setRAM();
    this.setCPU();
    this.setGPU();
    this.init();
  },
  data() {
    return {
      progress: 0,
      optionRAM: {
        xAxis: {
          data: [],
        },
        yAxis: {},
        series: [
          {
            type: 'line',
            data: [],
            symbolSize: 0,
          }
        ]
      },
      optionCPU: {
        xAxis: {
          data: [],
        },
        yAxis: {},
        series: [
          {
            type: 'line',
            data: [],
            symbolSize: 0,
          }
        ]
      },
      optionGPU: {
        xAxis: {
          data: [],
        },
        yAxis: {},
        series: [
          {
            type: 'line',
            data: [],
            symbolSize: 0,
          }
        ]
      }
    }
  },
  methods: {
    setRAM() {
      setInterval(()=> {
        let x = this.optionRAM.xAxis.data.length;
        this.optionRAM.xAxis.data.push(x);
        this.optionRAM.series[0].data.push(this.random());
        this.progress = x*5;
      }, 500)
    },
    setCPU() {
      setInterval(()=> {
        let x = this.optionCPU.xAxis.data.length;
        this.optionCPU.xAxis.data.push(x);
        this.optionCPU.series[0].data.push(this.random());
      }, 500)
    },
    setGPU() {
      setInterval(()=> {
        let x = this.optionGPU.xAxis.data.length;
        this.optionGPU.xAxis.data.push(x);
        this.optionGPU.series[0].data.push(this.random());
      }, 500)
    },
    random() {
      return Math.round(Math.random()*100)
    },
    init() {
      setTimeout(()=> {
        this.$store.commit('globalView/SET_appMode', 'training-done')
      }, 10000)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar-content {
    padding-top: 1rem;
    flex: 1;
  }
  .graf {
    height: 9rem;
    position: relative;
    background-color: $bg-workspace;
  }
</style>
