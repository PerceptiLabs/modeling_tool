<template lang="pug">
  section.sidebar-content
    .pc-chart_box
      span.pc-chart_title.big-text Progressbar
      .pc-chart_main
        sidebar-progress
    .pc-chart_box
      span.pc-chart_title.big-text RAM
      .pc-chart_main
        v-chart.pc-chart_chart(
          :auto-resize="true"
          theme="quantum"
          :options="optionRAM"
        )
    .pc-chart_box
      span.pc-chart_title.big-text CPU
      .pc-chart_main
        v-chart.pc-chart_chart(
          :auto-resize="true"
          theme="quantum"
          :options="optionCPU"
        )
    .pc-chart_box
      span.pc-chart_title.big-text GPU
      .pc-chart_main
        v-chart.pc-chart_chart(
          :auto-resize="true"
          theme="quantum"
          :options="optionGPU"
        )

</template>

<script>
import SidebarProgress from "./sidebar-progress";
//import ChartBase from "../charts/chart-base";

export default {
  name: "SidebarTraining",
  components: {SidebarProgress},
  mounted() {
    // this.setRAM();
    // this.setCPU();
    // this.setGPU();
  },
  beforeDestroy() {
    this.deleteTime();
  },
  data() {
    return {
      timer: {
        timeRam: ''
      },
      progress: 0,
      optionRAM: {
        grid: {
          top: '5',
          bottom: '25',
          right: '10',
          left: '30',
        },
        xAxis: {
          data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
        },
        series: [
          {
            type: 'line',
            data: [],
            symbolSize: 0,
          }
        ]
      },
      optionCPU: {
        grid: {
          top: '5',
          bottom: '25',
          right: '10',
          left: '30',
        },
        xAxis: {
          data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
        },
        series: [
          {
            type: 'line',
            data: [],
            symbolSize: 0,
          }
        ]
      },
      optionGPU: {
        grid: {
          top: '5',
          bottom: '25',
          right: '10',
          left: '30',
        },
        xAxis: {
          data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
        },
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
      this.timer.timeRam = setInterval(()=> {
        let x = this.optionRAM.xAxis.data.length;
        this.optionRAM.xAxis.data.push(x);
        this.optionRAM.series[0].data.push(this.random());
        this.progress = (x + 1)*10;
      }, 2000)
    },
    setCPU() {
      this.timer.timeCPU = setInterval(()=> {
        let x = this.optionCPU.xAxis.data.length;
        this.optionCPU.xAxis.data.push(x);
        this.optionCPU.series[0].data.push(this.random());
      }, 2000)
    },
    setGPU() {
      this.timer.timeGPU = setInterval(()=> {
        let x = this.optionGPU.xAxis.data.length;
        this.optionGPU.xAxis.data.push(x);
        this.optionGPU.series[0].data.push(this.random());
      }, 2000)
    },
    random() {
      return Math.round(Math.random()*100)
    },
    deleteTime() {
      clearInterval(this.timer.timeGPU);
      clearInterval(this.timer.timeCPU);
      clearInterval(this.timer.timeRam);
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
    height: 9rem;
    position: relative;
    background-color: $bg-workspace;
  }
  .pc-chart_chart {
    position: absolute !important;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 100%;
  }
</style>
