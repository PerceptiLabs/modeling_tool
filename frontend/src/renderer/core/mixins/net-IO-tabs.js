import {mapGetters} from "vuex";

const netIOTabs = {
  mounted() {
    this.inputsAndOutputs.map(el => {
      this.btnList[el.btnId] = el;
    });
    this.btnList['Global'] = {
      btnId: "Global",
      btnInteractiveInfo: {title: "Global", text: "Global"},
      layerId: null,
      layerType: null,
      name: "Global",
      type: "tab",
    }
  },
  data() {
    return {
      btnList: {}
    }
  },
  computed: {
    ...mapGetters({
      inputsAndOutputs: 'mod_workspace/GET_inputsAndOutputs',
    })
  },
}

export default netIOTabs;