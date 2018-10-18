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
    this.$refs.rootElement.addEventListener('mousedown', this.switchEvent);
    this.$refs.rootElement.addEventListener('touchstart', this.switchEvent);
  },

  beforeDestroy() {
    this.$refs.rootElement.removeEventListener('mousedown', this.switchEvent);
    this.$refs.rootElement.removeEventListener('touchstart', this.switchEvent);
  },
  computed: {
    active() {
      return this.dataEl.el.meta.isSelected
    },
    appMode() {
      return this.$store.state.globalView.appMode
    }
  },
  watch: {

  },
  methods: {
    switchEvent(ev) {
      if(this.appMode == 'edit') {
        this.bodyDown(ev)
      }
      else if (this.appMode == 'addArrow') {
        this.arrowStartPaint(ev)
      }
    },
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
