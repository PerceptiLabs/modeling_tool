const viewBoxMixin = {
  data() {
    return {
      idTimer: null,
      timeInterval: 1000,
    }
  },
  mounted() {
    //console.log('mounted');
    this.getStatistics()
  },
  beforeDestroy() {
    clearInterval(this.idTimer);
  },
};

export default viewBoxMixin
