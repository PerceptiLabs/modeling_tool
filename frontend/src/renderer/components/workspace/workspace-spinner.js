import {mapActions, mapGetters} from "vuex";
var unwatch;

const workspaceSpinner = {
  data() {
    return {
      counterHideSpinner: 0,
    }
  },
  computed: {
    ...mapGetters({
      doShowCharts:       'mod_workspace/GET_networkShowCharts',
      showTrainingSpinner:'mod_workspace/GET_showStartTrainingSpinner',
    })
  },
  watch: {
    showTrainingSpinner(newVal) {
      if(newVal) {
        unwatch = this.$watch('doShowCharts', this.watch_doShowCharts);
      }
      else {
        unwatch();
        if(this.isTutorialMode) this.pauseTraining();
      }
    },

  },
  methods: {
    ...mapActions({
      pauseTraining:        'mod_api/API_pauseTraining',
    }),
    watch_doShowCharts() {
      if (this.counterHideSpinner > 1) {
        this.set_showTrainingSpinner(false);
        this.counterHideSpinner = 0
      }
      else ++this.counterHideSpinner;
    },
  }
};

export default workspaceSpinner
