const netElementSettings = {
  data() {
    return {
      tabSelected: 0,
      tabs: []
    }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i;
    }
  }
};

export default netElementSettings

