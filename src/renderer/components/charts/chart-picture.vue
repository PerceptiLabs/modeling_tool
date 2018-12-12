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

  },
  data() {
    return {
      fullView: false,
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
      let imgH = img.height;
      let imgW = img.width;
      this.$refs.canvas.setAttribute('width', imgW);
      this.$refs.canvas.setAttribute('height', imgH);
      // let boxH = this.$refs.canvas.offsetParent.offsetWidth;
      // let boxW = this.$refs.canvas.offsetParent.offsetHeight;
      if(imgH/imgW >= 0) {
        this.$refs.canvas.style.minHeight = '100%';
      }
      else {
        this.$refs.canvas.style.width = '100%';
      }

      let canvas = this.$refs.canvas.getContext('2d');
      let imgData = canvas.createImageData(imgW, imgH);
      img.data.forEach((el, index) => imgData.data[index] = el);
      canvas.putImageData(imgData,0, 0);
    }
  },
  beforeDestroy() {
    //console.log('Destroy chart');
  }
}
</script>

<style lang="scss" scoped>
  .base-chart_main {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .chart-img {

  }
</style>
