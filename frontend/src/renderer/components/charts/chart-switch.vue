<template lang="pug">
  .base-chart(
    ref="baseChart"
    :class="{'full-view': fullView}"
  )
    .base-chart_head(v-if="!headerOff")
      .chart-head_title
        h5.ellipsis {{ chartLabel }}
        a.btn.save(type="button" ref="download" text="save" @click="saveChart")
          svg(width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M7.5 0C6.01664 0 4.5666 0.439867 3.33323 1.26398C2.09986 2.08809 1.13856 3.25943 0.570907 4.62987C0.00324965 6.00032 -0.145275 7.50832 0.144114 8.96318C0.433503 10.418 1.14781 11.7544 2.1967 12.8033C3.2456 13.8522 4.58197 14.5665 6.03683 14.8559C7.49168 15.1453 8.99968 14.9968 10.3701 14.4291C11.7406 13.8614 12.9119 12.9001 13.736 11.6668C14.5601 10.4334 15 8.98336 15 7.5C15 5.51088 14.2098 3.60322 12.8033 2.1967C11.3968 0.790176 9.48913 0 7.5 0V0ZM9.96032 12.3313H5.03969C4.87393 12.3313 4.71496 12.2654 4.59775 12.1482C4.48054 12.031 4.41469 11.872 4.41469 11.7063C4.41469 11.5405 4.48054 11.3815 4.59775 11.2643C4.71496 11.1471 4.87393 11.0813 5.03969 11.0813H9.96032C10.1261 11.0813 10.285 11.1471 10.4023 11.2643C10.5195 11.3815 10.5853 11.5405 10.5853 11.7063C10.5853 11.872 10.5195 12.031 10.4023 12.1482C10.285 12.2654 10.1261 12.3313 9.96032 12.3313V12.3313ZM10.4022 7.63L7.94 10.0938C7.8228 10.2109 7.66386 10.2767 7.49813 10.2767C7.3324 10.2767 7.17346 10.2109 7.05625 10.0938L4.59782 7.63563C4.48037 7.51843 4.4143 7.35939 4.41412 7.19348C4.41395 7.02756 4.47969 6.86838 4.59688 6.75094C4.71407 6.6335 4.87312 6.56742 5.03903 6.56724C5.20494 6.56707 5.36413 6.63281 5.48157 6.75L6.875 8.14344V2.61406C6.875 2.4483 6.94085 2.28933 7.05806 2.17212C7.17527 2.05491 7.33424 1.98906 7.5 1.98906C7.66576 1.98906 7.82473 2.05491 7.94195 2.17212C8.05916 2.28933 8.125 2.4483 8.125 2.61406V8.13969L9.51844 6.74625C9.63632 6.6324 9.79419 6.56941 9.95807 6.57083C10.1219 6.57225 10.2787 6.63798 10.3946 6.75386C10.5105 6.86974 10.5762 7.0265 10.5776 7.19037C10.579 7.35425 10.516 7.51212 10.4022 7.63V7.63Z" fill="#6185EE")
      .chart-head_meta
        button.btn.btn--link(type="button"
          :class="{'text-primary': fullView}"
          @click="toggleFullView"
        )
          svg(width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M14.5125 0.703125H3.4875C2.74913 0.703423 2.04109 0.996872 1.51898 1.51898C0.996872 2.04109 0.703423 2.74913 0.703125 3.4875V14.5125C0.703423 15.2509 0.996872 15.9589 1.51898 16.481C2.04109 17.0031 2.74913 17.2966 3.4875 17.2969H14.5125C15.2509 17.2966 15.9589 17.0031 16.481 16.481C17.0031 15.9589 17.2966 15.2509 17.2969 14.5125V3.4875C17.2966 2.74913 17.0031 2.04109 16.481 1.51898C15.9589 0.996872 15.2509 0.703423 14.5125 0.703125V0.703125ZM12.6039 9H11.7602V6.83663L6.83663 11.7602H9V12.6039H5.39606V9H6.23981V11.1634L11.1634 6.23981H9V5.39606H12.6039V9Z" fill="#6185EE")

    .base-chart_main(:style="styles.main")
      chart-spinner(v-if="showRequestSpinner" :invert="invertTheme")
      component(
        ref="chartArea"
        v-if="imgType.length"
        :is="componentName"
        :chart-label="chartLabel"
        :disable-header="disableHeader"
        :chart-data="imgData"
        :chartOptions="chartOptions",
        :custom-color="customColor"
        :chartIdx="chartIdx"
        @chartIdxChange="handleChartIdxChange"
        :enableDrag="enableDrag"
        :isFullView="fullView"
        :invert="invertTheme"
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
      chartIdx: {
        type: [Number],
        default: () => { 0 }
      },
      enableDrag: {
        type: Boolean,
        default: true
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
      invertTheme: {
        type: Boolean,
        default: false
      },
      disableHeader: {
        type: Boolean,
        default: false
      },
      showInitiallyRequestSpinner: {
        type: Boolean,
        default: true,
      },
      styles: {
        type: Object,
        default: function () {
          return {
            main: {},
          };
        },
      },
      chartOptions: {
        type: Object,
        default: function(){ return {} }
  }
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
        showRequestSpinner: this.showInitiallyRequestSpinner,
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
      handleChartIdxChange(chartIdx) {
        this.$emit('chartIdxChange', parseInt(chartIdx));
      }
    }
  }
</script>

<style lang="scss" scoped>
  .btn.save {
    margin-left: 8px;
  }

  .popup, .sidebar-setting-preview  {
    .btn.save {
      display: none;
    }
  }

  $border-color: theme-var($border-color);

  .base-chart {
    height: 100%;
    width: 100%;
    display: flex;
    overflow: hidden;
    flex-direction: column;
    background: $bg-workspace-3;
    //border-radius: 0 0 4px 4px;
    border-radius: 4px;
    border: 1px solid #9F9FA7;
    // padding: 20px 25px;

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
    margin: 2px 0;
  }
  section:not(#tutorial_statistics) {
    :not(ul + .info-section_main) {
      .base-chart_head {
        // background: #090f19;
        border-radius: 0px 0px 0px 0px;
        // margin: 0;
      }
    }

    ul + .info-section_main {
      .base-chart_head {
        // background: #3F4C70;
        border-radius: 0px 0px 0px 0px;
      }
    }
  }
  #tutorial_statistics {
    .info-section_main {
      .base-chart_head {
        // background: #090f19;
        border-radius: 0px 0px 0px 0px;
      }
    }
  } 
  .base-chart_main {
    position: relative;
    flex: 1 1 100%;
    min-height: 9rem;
    background: theme-var($neutral-8);
    padding-bottom: 10px;
  }
  .chart-head_title {
    display: flex;
    align-items: center;
    overflow: hidden;
    h5 {
      margin: 0;
      font-weight: 600;
      font-size: 14px;
      line-height: 16px;
      color: $color-6;
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
    color: $color-6;
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
