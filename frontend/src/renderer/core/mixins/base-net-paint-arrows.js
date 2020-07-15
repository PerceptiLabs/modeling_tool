const baseNetPaintArrows = {
  computed: {
    activeAction() {
      return this.$store.getters['mod_tutorials/getActiveAction']
    },
    wsZoom() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;
    },
    // Mix_paintArrow_startDrawArrow() {
    //   return this.$store.state.mod_workspace.startArrowID
    // },
    // Mix_paintArrow_preArrow() {
    //   return this.$store.state.mod_workspace.preArrow
    // }
  },
  watch: {
    networkMode(newVal) {
      newVal === 'addArrow'
        ? this.$refs.rootBaseElement.addEventListener('mouseup', this.Mix_paintArrow_arrowEndPaint)
        : this.$refs.rootBaseElement.removeEventListener('mouseup', this.Mix_paintArrow_arrowEndPaint);
    },
  },
  methods: {
    Mix_paintArrow_arrowStartPaint(ev) {
      ev.preventDefault();
      ev.stopPropagation();
      let el = this.dataEl;
      let layerSize = this.$parent.$parent.layerSize * this.wsZoom;

      this.$parent.$parent.addArrowListener();
      this.$store.commit('mod_workspace/SET_startArrowID', el.layerId);
      this.$store.commit('mod_workspace/SET_preArrowStart', {
        y: el.layerMeta.position.top + layerSize/2,
        x: el.layerMeta.position.left + layerSize/2
      });
    },
    Mix_paintArrow_arrowEndPaint(ev) {
      console.log("This is the event");
      ev.preventDefault();
      //ev.stopPropagation();
      this.$parent.$parent.removeArrowListener();
      this.$store.dispatch('mod_workspace/ADD_arrow', this.dataEl.layerId);
      this.$store.commit('mod_workspace/CLEAR_preArrow');
      this.$store.dispatch('mod_tutorials/pointActivate', {way: 'next', validation: this.activeAction.id});
      this.$store.dispatch('mod_api/API_updateNetworkSetting', this.dataEl.layerId);
    }
  }
}

export default baseNetPaintArrows
