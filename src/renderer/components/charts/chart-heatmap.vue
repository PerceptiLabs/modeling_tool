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
      let model = {
        tooltip: {},
        grid: {
          right: 50
        },
        xAxis: {
          boundaryGap: true,
          data: []
        },
        yAxis: {
          boundaryGap: true,
          data: []
        },
        visualMap: {
          min: -1.00,
          max: 1.00,
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
  watch: {
    // fullView(newVal, oldVal) {
    //   if(newVal) {
    //     console.log(this.$refs.chart);
    //     this.h = this.$refs.chart.$el.scrollHeight;
    //     this.w = this.$refs.chart.$el.scrollWidth;
    //     this.$refs.chart.resize(
    //       {
    //         width: 'auto',
    //         height: 'auto',
    //       }
    //     );
    //   }
    //   if (oldVal) {
    //     this.$refs.chart.resize({
    //       width: this.w,
    //       height: this.h,
    //     });
    //     //console.log(this.$refs.chart);
    //   }
    // }
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
