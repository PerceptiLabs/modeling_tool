<template lang="pug">
  .base-chart(
  :class="{'full-view': fullView}")
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
    this.canvasBox = this.$refs.canvas.getContext('2d');
    let imgH = this.chartData.length;
    let imgW = this.chartData[0].length;
    this.$refs.canvas.style.width = imgW;
    this.$refs.canvas.style.height = imgH;
    var imgData = this.canvasBox.createImageData(imgW, imgH);
    let floatData = this.chartData.reduce((sum, current)=> sum.concat(current),[]);
    let img = floatData.reduce((sum, current)=> {
        let ff = Math.round(current * 255);
        let rgba = [ff, ff, ff, 255];
        return sum.concat(rgba)
      },[]);
    for (var i=0;i<imgData.data.length; i+=4)
    {
      imgData.data[i+0]=img[i+0];
      imgData.data[i+1]=img[i+1];
      imgData.data[i+2]=img[i+2];
      imgData.data[i+3]=255;
    }
    this.canvasBox.putImageData(imgData,0, 0, 0, 0, 25, 25);
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
    //
    //   return
    // }
  },
  watch: {
    chartData(newData) {
      console.log('chartData watch');

    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    }
  },
  beforeDestroy() {
    //console.log('Destroy chart');
  }
}
</script>

<style lang="scss" scoped>
  .chart-img {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
  }
</style>
