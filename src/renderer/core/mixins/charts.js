const chartsMixin = {
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
    if(this.isNotPie) {this.createWWorker();}
    this.sendDataToWWorker();
    if(this.isNotPicture) {
      //this.$refs.chart.showLoading(this.chartSpinner);
      this.$refs.chart.resize();
      //window.addEventListener("resize", this.chartResize, false);
    }
  },
  beforeDestroy() {
    if(this.isNotPie) {
      this.wWorker.postMessage('close');
      this.wWorker.removeEventListener('message', this.drawChart, false);
    }
    if(this.isNotPicture && this.isNotPie) {
      this.$refs.chart.dispose();
      //window.removeEventListener("resize", this.chartResize, false);
    }
  },
  data() {
    return {
      chartModel: {},
      chartModelBuffer: null,
      fullView: false,
      wWorker: null,
      showRequestSpinner: true
    }
  },
  computed: {
    isNeedWait() {
      return this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent']
    },
    headerOff() {
      return this.$store.getters['mod_workspace/GET_testIsOpen'] || this.disableHeader;
    },
    doRequest() {
      return this.$store.getters['mod_workspace/GET_networkDoRequest']
    },
    doShowCharts() {
      return this.$store.getters['mod_workspace/GET_networkShowCharts']
    },
    isNotPicture() {
      return (this.$options._componentTag === "ChartPicture" || this.$options._componentTag === "chart-picture")
        ? false
        : true
    },
    isNotPie() {
      return (this.$options._componentTag === "ChartPie" || this.$options._componentTag === "chart-pie")
        ? false
        : true
    }
  },
  watch: {
    doShowCharts() {
      if(this.isNeedWait && this.chartModelBuffer) {
        if(this.isNotPicture) this.$refs.chart.hideLoading();
        this.chartModel = this.chartModelBuffer;
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
      if(newData) this.showRequestSpinner = false;
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView;
      //this.$nextTick(() => this.$refs.chart.resize());
    },
    drawChart(ev) {
      if(this.isNeedWait) this.chartModelBuffer = ev.data;
      else {
        this.$refs.chart.hideLoading();
        this.chartModel = ev.data;
      }
    },
    chartResize() {
      console.log(this.chartLabel);
      this.$refs.chart.resize()
    }
  }
};

export default chartsMixin
