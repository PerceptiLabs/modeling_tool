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
    if(this._name !== '<ChartPicture>') {
      this.$refs.chart.showLoading(this.chartSpinner);
      this.createWWorker();
      this.sendDataToWWorker();
      window.addEventListener("resize", this.chartResize, false);
      this.$refs.chart.resize();
    }
  },
  beforeDestroy() {
    if(this._name !== '<ChartPicture>') {
      this.wWorker.postMessage('close');
      this.wWorker.removeEventListener('message', this.drawChart, false);
      this.$refs.chart.dispose();
      window.removeEventListener("resize", this.chartResize, false);
    }
  },
  data() {
    return {
      chartModel: {},
      chartModelBuffer: {},
      fullView: false,
      wWorker: null,
    }
  },
  computed: {
    isNeedWait() {
      return this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent']
    },
    headerOff() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest || this.disableHeader;
    },
    doRequest() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.chartsRequest.doRequest
    }
  },
  watch: {
    doRequest(newVal) {
      if(newVal % 2 && this.isNeedWait) this.chartModel = this.chartModelBuffer;
    },
    '$store.state.mod_events.chartResize': {
      handler() {
        if(this._name !== '<ChartPicture>') {
          this.$nextTick(()=> this.$refs.chart.resize())
        }
      }
    },
    chartData(newData) {
      this.sendDataToWWorker(newData)
    },
    chartModel(data) {
      //console.log(this);
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView;
      this.$nextTick(() => this.$refs.chart.resize());
    },
    drawChart(ev) {
      //console.log('drawChart ', ev);
      this.isNeedWait
        ? this.chartModelBuffer = ev.data
        : this.chartModel = ev.data;
      this.$refs.chart.hideLoading()
    },
    chartResize() {
      this.$refs.chart.resize()
    }
  }
};

export default chartsMixin
