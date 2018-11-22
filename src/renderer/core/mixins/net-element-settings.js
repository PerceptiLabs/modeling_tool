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
    },
    // indexCurrentEl() {
    //   return this.$store.getters['globalView.getters/currentSelectedEl'].index
    // }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i;
    },
    applySettings() {
      this.$store.dispatch('mod_workspace/a_SET_elementSettings', this.settings)
    }
  }
};

export default netElementSettings

