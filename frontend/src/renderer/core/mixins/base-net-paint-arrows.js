const baseNetPaintArrows = {
  computed: {
    // $_paintArrow_startDrawArrow() {
    //   return this.$store.state.mod_workspace.startArrowID
    // },
    // $_paintArrow_preArrow() {
    //   return this.$store.state.mod_workspace.preArrow
    // }
  },
  watch: {
    networkMode(newVal) {
      newVal === 'addArrow'
        ? this.$refs.rootBaseElement.addEventListener('mouseup', this.$_paintArrow_arrowEndPaint)
        : this.$refs.rootBaseElement.removeEventListener('mouseup', this.$_paintArrow_arrowEndPaint);
    },
  },
  methods: {
    $_paintArrow_arrowStartPaint(ev) {
      ev.preventDefault();
      ev.stopPropagation();
      let el = this.dataEl;
      let layerSize = this.$parent.$parent.layerSize;

      this.$parent.$parent.addArrowListener();
      this.$store.commit('mod_workspace/SET_startArrowID', el.layerId);
      this.$store.commit('mod_workspace/SET_preArrowStart', {
        y: el.layerMeta.position.top + layerSize/2,
        x: el.layerMeta.position.left + layerSize/2
      });
    },
    $_paintArrow_arrowEndPaint(ev) {
      ev.preventDefault();
      //ev.stopPropagation();
      this.$parent.$parent.removeArrowListener();
      this.$store.dispatch('mod_workspace/ADD_arrow', this.dataEl.layerId);
      this.$store.commit('mod_workspace/CLEAR_preArrow')
    }
  }
}

export default baseNetPaintArrows
