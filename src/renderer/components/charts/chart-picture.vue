<template lang="pug">
  .base-chart(:class="{'full-view': fullView}")
    .base-chart_head(v-if="!headerOff")
      .chart-head_title
        h5.ellipsis {{ chartLabel }}
      .chart-head_meta
        button.btn.btn--link(type="button"
        :class="{'text-primary': fullView}"
        @click="toggleFullView")
          i.icon.icon-full-screen-graph
    .base-chart_main
      canvas.chart-img(ref="canvas")
</template>

<script>
  import {pathWebWorkers} from '@/core/constants.js'
  import chartMixin       from "@/core/mixins/charts.js";

export default {
  name: "ChartPicture",
  mixins: [chartMixin],
  data() {
    return {
      canvas2D: null
    }
  },
  watch: {
    doShowCharts() {
      if(this.chartModelBuffer) this.showImage(this.chartModelBuffer);
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    },
    createWWorker() {
      this.wWorker = new Worker(`${pathWebWorkers}/calcChartPic.js`);
      this.wWorker.addEventListener('message', this.drawChart, false);
      if(!this.canvas2D) this.canvas2D = this.$refs.canvas.getContext('2d');
    },
    sendDataToWWorker(dataWatch) {



      let data = dataWatch || this.chartData;
      if (!data) return;

      let dataImg = data.series[0];
      let imgH = dataImg.height;
      let imgW = dataImg.width;
      let canvasImg = this.canvas2D.createImageData(imgW, imgH);
      this.wWorker.postMessage({canvasImg, dataImg});
    },
    drawChart(ev) {
      this.isNeedWait
        ? this.chartModelBuffer = ev.data
        : this.showImage(ev.data);

      let stopCalDrow = new Date();
      let drawDelay = stopCalDrow - this.startCalDrow;
      console.log(`calc img delay`, `${drawDelay}ms`);
    },
    showImage(imgData) {
      
      let canvasEl = this.$refs.canvas;
      canvasEl.setAttribute('width', this.chartData.series[0].width);
      canvasEl.setAttribute('height', this.chartData.series[0].height);
      this.canvas2D.putImageData(imgData, 0, 0);
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .base-chart_main {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: $bg-workspace;
  }
  .chart-img {
    object-fit: contain;
    width: 100%;
    height: 100%;
  }
</style>
