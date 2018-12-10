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
      canvasBox: '',
      fullView: false,
      h: '',
      w: ''
    }
  },
  computed: {
    // chartModel() {
    //   return this.chartData[0];
    // }
  },
  watch: {
    chartData(newData) {
      //console.log(newData);
      // if(newData === null) {
      //   return
      // }
      this.drawPicture(newData[0].data)
    },
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    },
    drawPicture(img) {
      this.canvasBox = this.$refs.canvas.getContext('2d');
      // let imgH = this.chartModel.height;
      // let imgW = this.chartModel.width;
      let imgH = img.length;
      let imgW = img[0].length/4;
      // let boxH = this.$refs.canvas.offsetParent.offsetWidth;
      // let boxW = this.$refs.canvas.offsetParent.offsetHeight;
      this.$refs.canvas.setAttribute('width', imgW);
      this.$refs.canvas.setAttribute('height', imgH);
      if(imgH/imgW >= 0) {
        this.$refs.canvas.style.minHeight = '100%';
      }
      else {
        this.$refs.canvas.style.width = '100%';
      }

      let imgData = this.canvasBox.createImageData(imgW, imgH);
      let floatData = img.reduce((sum, current)=> sum.concat(current),[]);
      floatData.forEach((el, index) => imgData.data[index] = el);

      this.canvasBox.putImageData(imgData,0, 0);
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
