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
    name: "ChartBase",
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
        //type: Array,
        default: function () {
          return null
        }
      },
    },
    data() {
      return {
        fullView: false,
        h: '',
        w: '',
      }
    },
    computed: {
      chartModel() {
        let model = {
          tooltip: {},
          toolbox: {
            feature: {
              saveAsImage: {
                title: 'Save'
              },
              //magicType: {type: ['line', 'bar']},
            }
          },
          legend: {},
          yAxis: {},
          xAxis: {
            //boundaryGap: true,
          },
          series: []
        };
        if (this.chartData === null) {
          return model
        }
        if (this.chartData !== null && Array.isArray(this.chartData)) {
          model.series = this.chartData;

          let yLength = model.series[0].data.length;
          model.xAxis.data = [];
          for (var i = 0; i < yLength; i++) {
            model.xAxis.data.push(i);
          }
        }
        //(this.chartData !== null && typeof this.chartData === 'object')
        else {
          //model = {...model, ...this.chartData};
          model.legend.data = this.chartData.legend;
          model.series = this.chartData.series

          let yLength = model.series[0].data.length;
          model.xAxis.data = [];
          for (var i = 0; i < yLength; i++) {
            model.xAxis.data.push(i);
          }
        }
        return model
      }
    },
    watch: {},
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
  .base-chart_main {
    height: 300px;
  }
</style>
