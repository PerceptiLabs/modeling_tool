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
import chartMixin from "@/core/mixins/charts.js";

export default {
  name: "ChartPicture",
  mixins: [chartMixin],
  mounted() {
    this.canvas2D = this.$refs.canvas.getContext('2d');
    this.sendDataToWWorker(this.chartData);

  },
  data() {
    return {
      imgDataBuffer: null,
      canvas2D: null
    }
  },
  watch: {
    '$store.state.mod_events.chartsRequest.doRequest': {
      handler(newVal) {
        if(newVal % 2 && this.imgDataBuffer !== null) this.drawPicture(this.imgDataBuffer);
      }
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    },
    drawPicture(img) {
      let canvas2d = this.canvas2D;
      let canvas = this.$refs.canvas;
      // let imgH = img.height;
      // let imgW = img.width;
      let imgH = img.width;
      let imgW = img.height;
      canvas.setAttribute('width', imgW);
      canvas.setAttribute('height', imgH);
      let imgData = canvas2d.createImageData(imgW, imgH);
      img.data.forEach((el, index) => imgData.data[index] = el);
      canvas2d.putImageData(imgData,0, 0);
    },
    sendDataToWWorker(dataWatch) {
      let data = dataWatch || this.chartData;
      if (data === null || data === undefined) return;
      let dataImg = JSON.parse(JSON.stringify(data[0]));
      this.isNeedWait
        ? this.imgDataBuffer = dataImg
        : this.drawPicture(dataImg)
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
