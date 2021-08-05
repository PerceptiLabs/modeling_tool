const chartsMixin = {
  props: {
    chartData: {
      type: [Object, Array],
      default: function () {
        return null
      }
    },
    customColor: {
      type: Array
    },
    chartOptions: {
      type: Object,
      default: function(){ return {} }
    },
    isFullView: {
      type: Boolean,
      default: false
    }
  },
  
  created() {
    Object.keys(this.chartOptions).map(optionKey => {
      this.defaultModel[optionKey] = this.chartOptions[optionKey];
    })
    
    this.chartModel = this.defaultModel;
  },
  beforeMount() {
    if(this.isNotPicture) {
      this.applyCustomColor();
    }
  },
  mounted() {
    if(this.isNotPie) this.createWWorker();
    if(this.isNotPicture) {
      this.chartResize();
      //window.addEventListener("resize", this.chartResize, false);
    }
    this.sendDataToWWorker();
  },
  beforeDestroy() {
    if(this.isNotPie) {
      this.wWorker.postMessage('close');
      this.wWorker.removeEventListener('message', this.drawChart, false);
    }
    if(this.isNotPicture) {
      this.$refs.chart.dispose();
      //window.removeEventListener("resize", this.chartResize, false);
    }
  },
  data() {
    return {
      chartModel: {},
      chartModelBuffer: null,
      wWorker: null,
    }
  },
  computed: {
    isNeedWait() {
      return this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent']
    },
    doRequest() {
      return this.$store.getters['mod_workspace/GET_networkDoRequest']
    },
    doShowCharts() {
      return this.$store.getters['mod_workspace/GET_networkShowCharts']
    },
    isNotPicture() {
      return !(this.$options._componentTag === "ChartPicture" || this.$options._componentTag === "chart-picture")
    },
    isNotPie() {
      return !(this.$options._componentTag === "ChartPie" || this.$options._componentTag === "chart-pie")
    },
  },
  watch: {
    doShowCharts() {
      if(this.isNeedWait && this.chartModelBuffer && this.isNotPicture) {
        //if(this.isNotPicture) this.$refs.chart.hideLoading();
        this.$refs.chart.hideLoading();
        this.chartModel = this.chartModelBuffer;
        if(this.chartModelBuffer.series[0].type === 'pie') {
          this.$store.commit('mod_statistics/SET_piePercents', this.chartModel.series[0].data[0].value.toFixed())
        }
      }
    },
    // '$store.state.mod_events.chartResize': {
    //   handler() {
    //     if(this.isNotPicture) {
    //       this.$nextTick(()=> this.chartResize())
    //     }
    //   }
    // },
    chartData(newData, oldData) {
      this.sendDataToWWorker(newData);
    }
  },
  methods: {
    applyCustomColor() {
      if (this.customColor.length) {
        this.defaultModel.color = this.customColor;
      }
    },
    drawChart(ev) {
      this.$refs.chart.hideLoading();
      this.chartModel = ev.data;
    },
    chartResize() {
      this.$refs.chart.resize()
    }
  }
};

export default chartsMixin
