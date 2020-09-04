const baseNetPaintArrows = {
  computed: {
    activeAction() {
      return this.$store.getters['mod_tutorials/getActiveAction']
    },
    wsZoom() {
      return this.$store.getters['mod_workspace/GET_currentNetworkZoom'];
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
      const { outputDotId,outputLayerId } = ev.target.dataset;
      let el = this.dataEl;
      let currentTargerStartElement = document.querySelector(`[layer-id="${outputLayerId}"]`);
      let theDot = document.querySelector(`[data-output-circle-dot-id="${outputDotId}"][data-output-layer-id="${outputLayerId}"]`);

      const { x: layerWidth, y: layerHeight } = currentTargerStartElement.getBoundingClientRect();
      const { x: dotWidth, y: dotHeight } = theDot.getBoundingClientRect();
      const dotPositionWidth = (dotWidth - layerWidth);
      const dotPositionHeight = (dotHeight  - layerHeight) 


      this.$parent.$parent.addArrowListener();
      //  the start id should be setted as varid and layerid;
      // this.$store.commit('mod_workspace/SET_startArrowID', el.layerId);
      this.$store.commit('mod_workspace/SET_startArrowID', {
        outputDotId,
        outputLayerId,
        layerId: this.dataEl.layerId,
      });
      this.$store.dispatch('mod_workspace/SET_elementUnselect');
      this.$store.commit('mod_workspace/SET_preArrowStart', {
        y: (el.layerMeta.position.top + dotPositionHeight) + 3,
        x: (el.layerMeta.position.left + dotPositionWidth) + 3
      });
    },
    Mix_paintArrow_arrowEndPaint(ev) {
      ev.preventDefault();
      //ev.stopPropagation();
      const { inputDotId, inputLayerId } = ev.target.dataset;
      if(!inputDotId || !inputLayerId) {
        return;
      }
      this.$parent.$parent.removeArrowListener();
      this.$store.dispatch('mod_workspace/ADD_arrow', {
        inputDotId,
        inputLayerId,
        layerId: this.dataEl.layerId,
      }).then(() => {
        this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', this.dataEl.layerId);
      });
      this.$store.commit('mod_workspace/CLEAR_preArrow');
      this.$store.dispatch('mod_tutorials/pointActivate', {way: 'next', validation: this.activeAction.id});
      // this.$store.dispatch('mod_api/API_updateNetworkSetting', this.dataEl.layerId);
    }
  }
}

export default baseNetPaintArrows
