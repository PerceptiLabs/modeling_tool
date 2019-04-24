const baseNetPaintArrows = {
  data() {
    return {

    }
  },
  mounted() {

  },
  computed: {
    startDrawArrow() {
      return this.$store.state.mod_workspace.startArrowID
    },
    preArrow() {
      return this.$store.state.mod_workspace.preArrow
    }
  },
  watch: {
    networkMode(newVal) {
      if(newVal == 'addArrow') {
        this.$refs.rootBaseElement.addEventListener('mouseup', this.arrowEndPaint);
      }
      else {
        this.$refs.rootBaseElement.removeEventListener('mouseup', this.arrowEndPaint);
      }
    },
  },
  methods: {
    arrowStartPaint(ev) {
      ev.preventDefault();
      ev.stopPropagation();
      let el = this.dataEl.el;
      let layerSize = this.$parent.$parent.layerSize;

      this.$parent.$parent.addArrowListener();
      this.$store.commit('mod_workspace/SET_startArrowID', el.layerId);
      this.$store.commit('mod_workspace/SET_preArrowStart', {
        y: el.layerMeta.position.top + layerSize/2,
        x: el.layerMeta.position.left + layerSize/2
      });
    },
    arrowEndPaint(ev) {
      ev.preventDefault();
      ev.stopPropagation();
      this.$parent.$parent.removeArrowListener();
      this.$store.dispatch('mod_workspace/ADD_arrow', this.dataEl.el.layerId);
      this.$store.commit('mod_workspace/CLEAR_preArrow')
    }
  }
}

export default baseNetPaintArrows
