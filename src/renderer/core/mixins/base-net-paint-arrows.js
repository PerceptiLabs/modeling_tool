const baseNetPaintArrows = {
  data() {
    return {
      startArrowID: null
    }
  },
  mounted() {

  },
  computed: {

  },
  methods: {
    arrowStartPaint() {
      this.$store.commit('mod_workspace/SET_startArrowID', this.dataEl.el.layerId)
    },
    arrowMovePaint(ev) {
      //console.log('arrowMovePaint');
    },
    arrowEndPaint() {
      //this.$store.commit('mod_workspace/ADD_arrow', this.dataEl.el.layerId)
      this.$store.dispatch('mod_workspace/a_ADD_arrow', this.dataEl.el.layerId)
    }
  }
}

export default baseNetPaintArrows
