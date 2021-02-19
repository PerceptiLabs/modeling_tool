<template lang="pug">
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
      canvas2D: null,
      blinkCanv: false
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
      this.showImage(ev.data)

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
  .chart-img {
    object-fit: contain;
    width: 100%;
    height: 100%;
    max-height: 40vh;
    background: $bg-workspace;
  }
</style>
