<template lang="pug">
  .base-chart(
    ref="baseChart"
    :class="{'full-view': fullView}"
  )
    .base-chart_head(v-if="!headerOff")
      .chart-head_title
        h5.ellipsis {{ chartLabel }}
      .chart-head_meta
        button.btn.btn--link(type="button"
          :class="{'text-primary': fullView}"
          @click="toggleFullView"
        )
          i.icon.icon-full-screen-graph
    .base-chart_main
      request-spinner(v-if="showRequestSpinner")
      component(
        v-if="imgType.length"
        :is="componentName"
        :chart-label="chartLabel"
        :disable-header="disableHeader"
        :chart-data="imgData"
      )
      .base-chart_info(v-if="chartPieInfo.length") {{ chartInfo }}

</template>

<script>
  import ChartPicture     from "@/components/charts/chart-picture";
  import ChartBase        from "@/components/charts/chart-base";
  import ChartHeatmap     from "@/components/charts/chart-heatmap";
  import ChartPie         from "@/components/charts/chart-pie";
  import RequestSpinner   from '@/components/different/request-spinner.vue'

  export default {
    name: "ChartSwitch",
    components: {
      ChartHeatmap, ChartBase, ChartPicture, ChartPie,
      RequestSpinner },
    props: {
      chartLabel: {
        type: String,
        default: ''
      },
      chartData: {
        type: [Object, Array],
        default: function () {
          return null
        }
      },
      customColor: {
        type: Array,
        default: function () {
          return []
        }
      },
      disableHeader: {
        type: Boolean,
        default: false
      },
    },
    mounted() {

    },
    data() {
      return {
        imgType: '',
        imgData: null,
        showRequestSpinner: true,
        fullView: false,
      }
    },
    computed: {
      componentName() {
        switch (this.imgType) {
          case 'rgba':
            return 'ChartPicture';
          case 'line':
          case 'bar':
          case 'scatter':
            return 'ChartBase';
          case 'heatmap':
            return 'ChartHeatmap';
          case 'pie':
            return 'ChartPie';
        }
      },
      headerOff() {
        return this.$store.getters['mod_workspace/GET_testIsOpen'] || this.disableHeader;
      },
      chartPieInfo() {
        if(this.imgType === 'ChartPie'
          && this.chartModel.series
          && this.chartModel.series.length
          && typeof this.chartModel.series[0].data[0].value === 'number'

        ) {
          const info = this.chartModel.series[0].data[0].value.toFixed(2);
          return `${info}%`
        }
        return ''
      }
    },
    watch: {
      chartData(newVal) {
        if(newVal) {
          this.imgType = newVal.series[0].type;
          this.imgData = newVal;
          if(this.showRequestSpinner) {
            setTimeout(()=>{this.showRequestSpinner = false;}, 300)
          }
        }
        else {
          this.imgType = '';
          this.imgData = null
        }
      }
    },
    methods: {
      toggleFullView() {
        this.fullView = !this.fullView;
        //this.$nextTick(() => this.$refs.chart.resize());
      },
    }
  }
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .base-chart {
    width: 100%;
    display: flex;
    overflow: hidden;
    flex-direction: column;
  }
  .base-chart_head {
    display: flex;
    align-items: center;
    flex: 0 0 auto;
    justify-content: space-between;
    width: 100%;
    height: 3rem;
    padding: 0 1rem 0 2rem;
    background: $bg-window;
  }

  .chart-head_title {
    overflow: hidden;
    h5 {
      margin: 0;
    }
  }
  .base-chart_info {
    font-size: 2rem;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    .full-view & {
      z-index: 3;
    }
  }
</style>