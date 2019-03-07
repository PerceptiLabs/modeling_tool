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
      window.addEventListener("resize", ()=> { this.$refs.chart.resize()}, false);
      this.$refs.chart.resize();
    }
  },
  beforeDestroy() {
    if(this._name !== '<ChartPicture>') {
      this.wWorker.postMessage('close');
      this.wWorker.removeEventListener('message', this.drawChart, false);
      this.$refs.chart.dispose();
      window.removeEventListener("resize", ()=> { this.$refs.chart.resize()}, false);
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
      return this.$store.state.mod_events.chartsRequest.waitGlobalEvent
    },
    headerOff() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest || this.disableHeader;
    }
  },
  watch: {
    '$store.state.mod_events.chartsRequest.doRequest': {
      handler(newVal) {
        if(newVal % 2) this.chartModel = this.chartModelBuffer;
      }
    },
    '$store.state.mod_events.chartResize': {
      handler() {
        if(this._name !== '<ChartPicture>') this.$refs.chart.resize();
      }
    },
    chartData(newData) {
      this.sendDataToWWorker(newData)
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView;
      this.$nextTick(() => this.$refs.chart.resize());
    },
    drawChart(ev) {
      this.isNeedWait
        ? this.chartModelBuffer = ev.data
        : this.chartModel = ev.data;
      this.$refs.chart.hideLoading()
    }
  }
};

export default chartsMixin
