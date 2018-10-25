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
    this.$refs.rootBaseElement.addEventListener('mousedown', this.switchEvent);
    this.$refs.rootBaseElement.addEventListener('touchstart', this.switchEvent);
  },

  beforeDestroy() {
    this.$refs.rootBaseElement.removeEventListener('mousedown', this.switchEvent);
    this.$refs.rootBaseElement.removeEventListener('touchstart', this.switchEvent);
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
    appMode(newVal) {
      if(newVal == 'addArrow') {
        this.$parent.$parent.$el.addEventListener('mousemove', this.arrowMovePaint);
        this.$refs.rootBaseElement.addEventListener('mouseup', this.arrowEndPaint);

        this.$parent.$parent.$el.addEventListener('touchmove', this.arrowMovePaint, true);
        this.$refs.rootBaseElement.addEventListener('touchend touchcancel', this.arrowEndPaint, true);
        this.$refs.rootBaseElement.addEventListener('touchstart', this.arrowEndPaint, true);
      }
      else {
        this.$parent.$parent.$el.removeEventListener('mousemove', this.arrowMovePaint);
        this.$refs.rootBaseElement.removeEventListener('mouseup', this.arrowEndPaint);

        this.$parent.$parent.$el.removeEventListener('touchmove', this.arrowMovePaint, true);
        this.$refs.rootBaseElement.removeEventListener('touchend touchcancel', this.arrowEndPaint, true);
        this.$refs.rootBaseElement.removeEventListener('touchstart', this.arrowEndPaint, true);
      }
    }
  },
  methods: {
    switchEvent(ev) {
      ev.stopPropagation();
      if(this.appMode == 'edit' && !this.isLock) {
        this.setFocusEl(ev);
        this.bodyDown(ev)
      }
      else if (this.appMode == 'addArrow' && !this.isLock) {
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
    setFocusEl(ev) {
      if(ev.ctrlKey) {
        this.$store.commit('mod_workspace/SET_metaMultiSelect', { path: [this.dataEl.index], setValue: true });
      }
      else {
        this.ClickElementTracking = ev.target.closest('.clickout');
        document.addEventListener('click', this.clickOutside);
        this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: true });
      }
    },
    hideAllWindow() {
      this.settingsIsOpen = false;
      this.contextIsOpen = false;
    },
    deselect() {
      this.hideAllWindow();
      this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: false });
    },

  }
};

export default baseNetFunctional
