const netElementSettings = {
  data() {
    return {
      tabSelected: 0,
      tabs: ['Settings', 'Code'],
    }
  },
  computed: {
    userMode() {
      return this.$store.state.globalView.userMode
    }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i;
    }
  }
};

export default netElementSettings

