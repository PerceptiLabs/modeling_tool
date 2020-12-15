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
      a.btn.save(type="button" ref="download" text="save" @click="saveChart")
        i.icon.icon-download
      chart-spinner(v-if="showRequestSpinner")
      component(
        ref="chartArea"
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
    created() {
      this.imgType = '';
      this.imgData = null;
    },
    mounted() {
      if(this.chartData && this.chartData.series && this.chartData.series.length) {
        this.imgType = this.chartData.series[0].type;
        this.imgData = this.chartData;
        if(this.showRequestSpinner) {
          setTimeout(()=>{this.showRequestSpinner = false}, 300)
        }
      }
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
          return  waitInfo ? `${waitInfo}%` : this.chartData.series[0].data[0].value.toFixed() + '%'
        }
        return ''
      },
      viewType() {
        return this.$store.getters['mod_workspace/GET_viewType'];
      },
      nextSampleClicker() {
        return this.$store.state.mod_events.componentEvents.test.nextSampleClick;
      },
    },
    watch: {
      nextSampleClicker: {
        handler() {
          this.imgType = '';
          this.imgData = null;
          this.showRequestSpinner = true;
        }
      },
      chartData(newVal) {
        if(newVal && newVal.series && newVal.series.length) {
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
      viewType: {
        handler(newVal, oldVal) {
          if (newVal === 'test') {
            this.imgType = '';
            this.imgData = null;
            this.showRequestSpinner = true;
          }
        },
        immediate: true
      }
    },
    methods: {
      saveChart() {
        const component = this.$refs['chartArea'].$el
        const canvas = component.querySelector('canvas');
        const url = canvas.toDataURL("image/png")

        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'Export.png') //or any other extension
        document.body.appendChild(link)
        link.click()
      },
      toggleFullView() {
        this.fullView = !this.fullView;
        //this.$nextTick(() => this.$refs.chart.resize());
      },
    }
  }
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .btn.save {
    width: 21px;
    height: 21px;   
    position: absolute;
    background: #2E3A5A;
    border-radius: 2px;
    border: 1px solid #5E6F9F;
    color: $toolbar-button-border;
    right: 7px;
    bottom: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
  }

  .popup, .sidebar-setting-preview  {
    .btn.save {
      display: none;
    }
  }

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
    border: 1px solid rgba(97, 133, 238, 0.4);
    border-radius: 2px 2px 0px 0px;
    
    background: #3F4C70;
    border-bottom: 1px solid $border-color;
  }
  section:not(#tutorial_statistics) {
    :not(ul + .info-section_main) {
      .base-chart_head {
        background: #090f19;
        border-radius: 0px 0px 0px 0px;
      }
    }

    ul + .info-section_main {
      .base-chart_head {
        background: #3F4C70;
        border-radius: 0px 0px 0px 0px;
      }
    }
  }
  #tutorial_statistics {
    .info-section_main {
      .base-chart_head {
        background: #090f19;
        border-radius: 0px 0px 0px 0px;
      }
    }
  } 
  .base-chart_main {
    position: relative;
    flex: 1 1 100%;
    min-height: 9rem;
    background: #212839;
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

  .data-settings_chart {
    &.base-chart {
      border: none;
    }
    .base-chart_main {
      min-height: 140px;
      display: flex;
      align-items: center;
      canvas {
        max-height: 140px;
      }
    }
  }

</style>
