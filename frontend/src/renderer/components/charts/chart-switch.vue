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
      chart-spinner(v-if="showRequestSpinner")
      component(
        v-if="imgType.length"
        :is="componentName"
        :chart-label="chartLabel"
        :disable-header="disableHeader"
        :chart-data="imgData"
        :custom-color="customColor"
      )
      .base-chart_info(v-if="chartPieInfo.length") {{ chartPieInfo }}

</template>

<script>
  import ChartPicture     from "@/components/charts/chart-picture";
  import ChartBase        from "@/components/charts/chart-base";
  import ChartHeatmap     from "@/components/charts/chart-heatmap";
  import ChartPie         from "@/components/charts/chart-pie";
  import ChartSpinner     from '@/components/charts/chart-spinner'

  export default {
    name: "ChartSwitch",
    components: {
      ChartHeatmap, ChartBase, ChartPicture, ChartPie,
      ChartSpinner
    },
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
        return this.disableHeader;
//        return this.$store.getters['mod_workspace/GET_testIsOpen'] || this.disableHeader;
      },
      statusNetworkCore() {//mod_workspace/GET_networkCoreStatus
        return this.$store.getters['mod_workspace/GET_networkCoreStatus'];
      },
      chartPieInfo() {
        if(this.imgType === 'pie'
          && typeof this.chartData.series[0].data[0].value === 'number'
        ) {
          let waitInfo = this.$store.state.mod_statistics.piePercents;
          if(this.statusNetworkCore === 'Finished') return `${this.chartData.series[0].data[0].value.toFixed()}%`;
          return  waitInfo ? `${waitInfo}%` : ''
        }
        return ''
      }
    },
    watch: {
      statusNetworkCore(newVal) {
        //console.log(newVal)
      },
      chartData(newVal) {
        if(newVal) {
          this.imgType = newVal.series[0].type;
          this.imgData = newVal;
          if(this.showRequestSpinner) {
            setTimeout(()=>{this.showRequestSpinner = false}, 300)
          }
        }
        else {
          this.imgType = '';
          this.imgData = null
        }
      },
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

  $border-color: rgba(97, 133, 238, 0.4);

  .base-chart {
    width: 100%;
    display: flex;
    overflow: hidden;
    flex-direction: column;
    background: $bg-workspace-3;
    border: 1px solid $border-color;

    &.full-view {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      z-index: 3;
    }
  }
  .base-chart_head {
    display: flex;
    align-items: center;
    flex: 0 0 auto;
    justify-content: space-between;
    width: 100%;
    height: 2.5rem;
    padding: 0 1rem 0 1rem;
    background: #090f19;
    border-bottom: 1px solid $border-color;
  }
  .base-chart_main {
    position: relative;
    flex: 1 1 100%;
    min-height: 9rem;
    background: #222939;
  }
  .chart-head_title {
    overflow: hidden;
    h5 {
      margin: 0;
      font-family: Nunito Sans;
      font-style: normal;
      font-weight: 600;
      font-size: 11px;
      line-height: 15px;
      color: #B6C7FB;
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
  .chart-head_meta i {
    font-size: 1.3rem;
  }
  .icon-full-screen-graph {
    color: #B6C7FB;
  }
</style>
