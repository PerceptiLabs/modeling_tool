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
    appMode(newVal) {
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
      console.log('arrowStartPaint');
      ev.preventDefault();
      ev.stopPropagation();
      let el = this.dataEl.el;
      this.$parent.$parent.addArrowListener();
      this.$store.commit('mod_workspace/SET_startArrowID', el.layerId)
    },
    arrowEndPaint(ev) {
      console.log('arrowEndPaint');
      ev.preventDefault();
      ev.stopPropagation();
      this.$parent.$parent.removeArrowListener();
      this.$store.dispatch('mod_workspace/a_ADD_arrow', this.dataEl.el.layerId)
    },
  }
}

export default baseNetPaintArrows
