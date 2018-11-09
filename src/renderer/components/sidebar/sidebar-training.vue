<template lang="pug">
  section.sidebar-content
    .pc-chart_box
      span.pc-chart_title.big-text Progressbar
      .pc-chart_main
        sidebar-progress(:percent="progress")
    .pc-chart_box
      span.pc-chart_title.big-text RAM
      .pc-chart_main
        chart-line(
          :headerOff="true"
          :chartData="optionRAM")
    .pc-chart_box
      span.pc-chart_title.big-text CPU
      .pc-chart_main
        chart-line(
        :headerOff="true"
        :chartData="optionCPU")
    .pc-chart_box
      span.pc-chart_title.big-text GPU
      .pc-chart_main
        chart-line(
        :headerOff="true"
        :chartData="optionGPU")

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
        this.$store.dispatch('globalView/NET_trainingDone')
      }, 10000)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar-content {
    padding-top: 1rem;
    flex: 0 0 auto;
    display: flex;
    flex-wrap: wrap;
  }

  .pc-chart_box {
    width: 100%;
    flex: 0 0 100%;
  }

  .pc-chart_title {
    display: block;
    margin: 1rem 0 .5rem;
  }
  .pc-chart_main {
    display: flex;
    justify-content: center;
    height: 9rem;
    position: relative;
    background-color: $bg-workspace;
  }

</style>
