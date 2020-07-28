const netElementViewLayer = {
  props: {
    draggable: {
      type: Boolean,
      default: false
    },
    currentEl: {
      type: Object,
    },
    showTitle: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    layerStyles() {
      if(!this.currentEl) return;
      return {
        'background': this.currentEl.layerMeta.layerBgColor.length ? this.currentEl.layerMeta.layerBgColor : null
      }
    }
  },
};

export default netElementViewLayer

