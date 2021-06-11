import {mapGetters} from "vuex";

const netIOTabs = {
  mounted() {
    this.inputsAndOutputs.map(el => {
      this.btnList[el.btnId] = el;
    });
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