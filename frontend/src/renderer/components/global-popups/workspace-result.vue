<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup-background
        .popup_tab-set
          .popup_header.disable
            h3 Result
        .popup_body
          .settings-layer_section
            .body_results-info.d-flex
              .column-item(v-for="(columData, index) in popupInfo")
                p.header {{Object.keys(columData)[0]}}
                .lists(v-for="lists in columData")
                  .list-item.d-flex(v-for="(list, index) in lists")
                    p(style="margin-right: 3px") {{index}}:  
                    p {{list.toFixed(2)}}

        .popup_foot
          //-button.btn.btn--primary(type="button"
            @click="closePopup()") Cancel
          button.btn.btn--primary.tutorial-relative(type="button"
            id="tutorial_run-test-button"
            @click="runTest") Run test
</template>

<script>
import { mapState, mapActions } from 'vuex';
export default {
  name: "GeneralResult",
  mounted() {
    this.$store.dispatch('mod_api/API_getResultInfo')
      .then((data)=> {

        // TOREMOVE
        delete data['consoleLogs']
        this.popupInfo = {...data};
      });
  },
  data() {
    return {
      popupInfo: {
      }
    }
  },
  methods: {
    ...mapActions({
      setCurrentView:           'mod_tutorials/setCurrentView'
    }),
    runTest() {
      this.closePopup();
      this.$store.dispatch('mod_workspace/SET_statusNetworkCoreStatusProgressClear');
      this.$store.dispatch('mod_workspace/SET_elementUnselect');
      this.$store.dispatch("mod_workspace/SET_currentTestIndex", this.currentNetworkIndex);      
      this.$store.dispatch('mod_workspace/SET_openTest', true);
      this.$store.dispatch('mod_workspace/setViewType', 'test');
      this.setCurrentView('tutorial-test-view');
    },
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
      this.$store.dispatch('mod_workspace/SET_netMode', 'edit');
    },
    toFixedWithMaxDigits(value, maxDigits) {
      return value.toFixed(maxDigits).replace('.00', '');
    }
  },
  computed: {
    ...mapState({
      currentNetworkIndex:           state => state.mod_workspace.currentNetwork,
    }),
    trainingTargetMetric() {

      if (this.popupInfo.acc_train) {
        return `Training Accuracy: ${ this.toFixedWithMaxDigits(this.popupInfo.acc_train, 2) }%`;
      }
      
      if (this.popupInfo.r_sq_train) {
        return `Training R Squared:  ${ this.toFixedWithMaxDigits(this.popupInfo.r_sq_train / 100, 2) }`;
      }

      return `Training Accuracy: 0%`;
    },
    validationTargetMetric() {

      if (this.popupInfo.acc_val) {
        return `Validation Accuracy: ${ this.toFixedWithMaxDigits(this.popupInfo.acc_val, 2) }%`;
      }
      
      if (this.popupInfo.r_sq_val) {
        return `Validation R Squared:  ${ this.toFixedWithMaxDigits(this.popupInfo.r_sq_val / 100, 2) }`;
      }

      return `Validation Accuracy: 0%`;
    },
  }
}
</script>

<style lang="scss" scoped>
  .body_results-info {
    font-size: 1.2rem;
    padding: 0 1rem;
    display: flex;
    margin-bottom: 2rem;
    line-height: 1.6;

    .column-item {
      width: 200px;

      .header {
        margin-top: 20px;
        margin-bottom: 25px;
        font-weight: 500;
        font-size: 1.3rem
      }
    }
    span {
      display: block;
    }
    .results-info--validation {
      margin-right: 1rem;
    }
  }
</style>
