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
    document.documentElement.addEventListener('mousedown', this.deselect);
    // this.$refs.el.addEventListener("focus", (event)=> {
    //   console.log('focus')
    //   document.addEventListener('keydown', (event) => {
    //     const keyName = event.key;
    //     alert('keydown event\n\n' + 'key: ' + keyName);
    //   });
    // }, false);
    // document.addEventListener('keydown', (event) => {
    //   const keyName = event.key;
    //   alert('keydown event\n\n' + 'key: ' + keyName);
    // });
  },
  beforeDestroy() {
    document.documentElement.removeEventListener('mousedown', this.deselect);
  },
  computed: {
    active() {
      return this.dataEl.el.meta.isSelected
    }
  },
  watch: {
    // active(isActive) {
    //   if (isActive) {
    //     //this.$emit('activated');
    //   } else {
    //     //this.$emit('deactivated');
    //     this.hideAllWindow();
    //   }
    // },

    // isActive(val) {
    //   this.active = val;
    // },
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
    clickEl() {
      //console.log('clickEl')
    },
    setFocusBtn() {
      this.$refs.btn.focus();
      this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: true });
    },
    deselect() {
      // if (this.preventActiveBehavior) {
      //   return
      // }
      this.hideAllWindow();
      this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: false });
    },
  }
};

export default baseNetFunctional
