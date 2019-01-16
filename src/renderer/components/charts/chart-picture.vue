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


export default {
  name: "ChartPicture",
  props: {
    headerOff: {
      type: Boolean,
      default: false
    },
    chartLabel: {
      type: String,
      default: ''
    },
    chartData: {
      type: Array,
      default: function() {
        return null
      }
    },
  },
  mounted() {
    this.canvas2D = this.$refs.canvas.getContext('2d');
  },
  data() {
    return {
      fullView: false,
      canvas2D: null
    }
  },
  watch: {
    chartData(newData) {
      this.drawPicture(newData[0])
    },
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    },
    drawPicture(img) {
      let canvas2d = this.canvas2D;
      let canvas = this.$refs.canvas;
      let imgH = img.height;
      let imgW = img.width;
      canvas.setAttribute('width', imgW);
      canvas.setAttribute('height', imgH);
      if(imgH/imgW >= 1) {
        this.$refs.canvas.style.minHeight = '100%';
      }
      else {
        this.$refs.canvas.style.width = '100%';
      }
      let imgData = canvas2d.createImageData(imgW, imgH);
      img.data.forEach((el, index) => imgData.data[index] = el);
      canvas2d.putImageData(imgData,0, 0);
    }
  },
  beforeDestroy() {
    //console.log('Destroy chart');
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
</style>
