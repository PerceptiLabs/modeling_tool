<template lang="pug">
  .chart-wrapper(
    @mouseenter="isHovering = true"
    @mouseleave="isHovering = false")
    img.left-arrow.shadow(v-if="isMultiSeriesData && isHovering"
      src='../../../../static/img/chart-preview/left-caret.svg' 
      @click="handleArrowClick(-1)")
    img.right-arrow.shadow(v-if="isMultiSeriesData && isHovering"
      src='../../../../static/img/chart-preview/right-caret.svg' 
      @click="handleArrowClick(1)")
    .slider(v-if="isMultiSeriesData && isHovering")
      input(type="range" 
        min="0"
        :max="numFeatures - 1"
        :value="chartIdx"
        @input="handleSliderChange"
        @mousedown="handleMouseDown")
      .selector(ref='selector' :style="rangeToolTipStyle")
        .selector-btn
        .selector-tooltip
          span {{ chartIdx + 1}}
    canvas.chart-img(ref="canvas" :class="{'is-full-view': isFullView, 'invert': invert}")
</template>

<script>
  import {pathWebWorkers} from '@/core/constants.js'
  import chartMixin       from "@/core/mixins/charts.js";

export default {
  name: "ChartPicture",
  mixins: [chartMixin],
  props: {
    chartIdx: {
      type: [Number],
      default: function () {
        return 0
      }
    },
    invert: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      canvas2D: null,
      blinkCanv: false,
      isHovering: false
    }
  },
  computed: {
    isMultiSeriesData() {
      if (!this.chartData || !this.chartData.series || this.chartData.series.length <= 1) {
        return false;
      }

      return true;
    },
    numFeatures() {
      let numFeatures = 1;
      if (this.chartData && this.chartData.series) {
        numFeatures = this.chartData.series.length;
      }

      return numFeatures;
    },
    rangeToolTipStyle() {
      return {
        left: `${this.chartIdx / (this.numFeatures - 1) * 100}%`
      }
    }
  },
  watch: {
    doShowCharts() {
      if(this.chartModelBuffer) this.showImage(this.chartModelBuffer);
    },
    chartIdx(newVal, oldVal) {
      this.sendDataToWWorker();
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView;
    },
    createWWorker() {
      this.wWorker = new Worker(`${pathWebWorkers}/calcChartPic.js`);
      this.wWorker.addEventListener('message', this.drawChart, false);
      if(!this.canvas2D) this.canvas2D = this.$refs.canvas.getContext('2d');
    },
    sendDataToWWorker(dataWatch) {
      let data = dataWatch || this.chartData;
      if (!data) return;

      let dataImg = data.series[this.chartIdx];
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
      canvasEl.setAttribute('width', this.chartData.series[this.chartIdx].width);
      canvasEl.setAttribute('height', this.chartData.series[this.chartIdx].height);
      this.canvas2D.putImageData(imgData, 0, 0);
    },
    handleArrowClick(skipAmount) {
      if (typeof skipAmount !== 'number') { return; }

      const newChartIdx = ((skipAmount + this.chartIdx % this.numFeatures) + this.numFeatures) % this.numFeatures;
      this.updateSlider(newChartIdx);

      this.$emit('chartIdxChange', newChartIdx);
    },
    handleSliderChange(ev) {      
      this.$store.commit('mod_events/set_isChartFeatureSliderDragEvent', false);

      this.updateSlider(ev.target.value);

      this.$emit('chartIdxChange', ev.target.value);
    },
    handleMouseDown(ev) {
      this.$store.commit('mod_events/set_isChartFeatureSliderDragEvent', true);
    },
    updateSlider(value) {
      if (this.$refs['selector']) {
        this.$refs['selector'].style.left = `${value / (this.numFeatures - 1) * 100}%`;
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  .chart-wrapper {
    height: 100%;
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .left-arrow {
    position: absolute;
    top: 45%;
    left: 5%;
    transform: translateY(-50%);
    cursor: pointer;
  }

  .right-arrow {
    position: absolute;
    top: 45%;
    right: 5%;
    transform: translateY(-50%);
    cursor: pointer;
  }

  .slider {
    position: absolute;
    height: 1rem;
    margin: 0 7.5%;
    width: 85%;
    bottom: 10%;

    display: flex;
    justify-content: center;
    align-items: center;

    input[type='range'] {
      -webkit-appearance: none;
      background: #808080;
      border-radius: 5px;
      height: 0.4rem;
      padding: 0;
      width: 100%;
      z-index: 2;

      &::-webkit-slider-thumb {
        -webkit-appearance: none;
        border-radius: 50%;
        cursor: ew-resize;
        height: 2rem;
        width: 2rem;
        z-index: 3;
        position: relative;
      }

      &::-moz-range-thumb {
        -webkit-appearance: none;
        border-radius: 50%;
        cursor: ew-resize;
        height: 2rem;
        width: 2rem;
        z-index: 3;
        position: relative;
      }
    }

    .selector {
      bottom: 10%;
      height: 3.5rem;
      left: 50%;
      pointer-events: none;
      position: absolute;
      transform: translateX(-50%);
      width: 1rem;
      z-index: 2;

      .selector-btn {
        background: white;
        height: 1rem;
        border-radius: 50%;
        bottom: 0;
        position: absolute;
        width: 1rem;

        -moz-box-shadow: 0 0 3px rgba(0, 0, 0, .7);
        -webkit-box-shadow: 0 0 3px rgba(0, 0, 0, .7);
        box-shadow: 0 0 3px rgba(0, 0, 0, .7);
      }

      .selector-tooltip {
        background: $color-6;
        box-sizing: border-box;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        text-align: center;
        line-height: 18px;
        font-size: 14px;
        color: white;
        left: 50%;
        // padding: 0.3rem;
        pointer-events: none;
        position: absolute;
        transform: translateX(-50%);
        top: 0;
      }
    }
  }

  .chart-img {
    
    &.invert {
      background: $bg-setting-layer;
    }
    display: block;
    max-height: 40vh;
    object-fit: contain;
    width: 100%;
    height: 100%;
    &.is-full-view {
      max-height: 100vh;
    }
  }

  .shadow {
    filter: drop-shadow( 0px 0px 3px rgba(0, 0, 0, .7));
  }
</style>
