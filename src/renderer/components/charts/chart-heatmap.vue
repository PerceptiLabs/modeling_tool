<template lang="pug">
  .base-chart(
  ref="baseChart"
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
      v-chart(
      ref="chart"
      :auto-resize="true"
      theme="quantum"
      :options="chartModel"
      )
</template>

<script>
export default {
  name: "ChartHeatmap",
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
  data() {
    return {
      fullView: false,
      h: '',
      w: ''
    }
  },
  computed: {
    chartModel() {
      let valArr = this.chartData[0].data.map((num)=> num[2]);
      let size = Math.sqrt(this.chartData[0].data.length);
      let axios = [];
      for (var i = 0; i <= size-1; i++) {
        axios.push(i)
      }
      let model = {
        tooltip: {},
        grid: {
          right: 50
        },
        xAxis: {
          boundaryGap: true,
          data: axios
        },
        yAxis: {
          boundaryGap: true,
          data: axios
        },
        visualMap: {
          min: Math.min(...valArr),
          max: Math.max(...valArr),
          top: '10px',
          itemHeight: 300,
          realtime: false,
          left: 'right',
        },
        series: []
      };
      if(this.chartData !== null) {
        model.series = this.chartData;
      }
      return model
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    }
  },
  beforeDestroy() {
    //console.log('Destroy chart');
    this.$refs.chart.destroy();
  }
}
</script>

<style lang="scss" scoped>

</style>
