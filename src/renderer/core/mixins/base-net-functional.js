const baseNetFunctional = {
  props: {
    dataEl: {
      type: Object,
      default: function () {
        return {}
      }
    },
  },
  data() {
    return {
      contextIsOpen: false,
      settingsIsOpen: false,
    }
  },
  mounted() {

  },
  beforeDestroy() {

  },
  computed: {
    active() {
      return this.dataEl.el.meta.isSelected
    }
  },
  watch: {

  },
  methods: {
    openSettings() {
      this.hideAllWindow();
      this.settingsIsOpen = true;
    },
    openContext() {
      this.hideAllWindow();
      this.contextIsOpen = true;
    },
    hideAllWindow() {
      this.settingsIsOpen = false;
      this.contextIsOpen = false;
    },
    blurElement() {
      this.deselect();
    },
    setFocusBtn() {
      this.$refs.btn.focus();
      this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: true });
    },
    deselect() {
      this.hideAllWindow();
      this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: false });
    },
  }
};

export default baseNetFunctional
