<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header.disable
          h3 Result
      .popup_body
        .settings-layer_section
          .body_results-info
            .results-info--validation
              p Training
              span {{ trainingTargetMetric }}
              span Training Loss: {{ popupInfo.loss_train | round(2)}}
            .results-info--validation
              p Validation
              span {{ validationTargetMetric }}
              span Validation Loss: {{ popupInfo.loss_val | round(2)}}

      .popup_foot
        //-button.btn.btn--primary(type="button"
          @click="closePopup()") Cancel
        button.btn.btn--primary.tutorial-relative(type="button"
          id="tutorial_run-test-button"
          @click="runTest") Run test
</template>

<script>
import { mapActions } from 'vuex';
export default {
  name: "GeneralResult",
  mounted() {
    this.$store.dispatch('mod_api/API_getResultInfo')
      .then((data)=> {
        this.popupInfo = {...data};
      });
    this.tutorialPointActivate({way: 'next', validation: 'tutorial_statistic-tab'})
  },
  data() {
    return {
      popupInfo: {
        acc_train: 0,
        r_sq_train: 0,
        loss_train: 0,
        acc_val: 0,
        r_sq_val: 0,
        loss_val: 0,
      }
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    runTest() {
      this.closePopup();
      this.$store.dispatch('mod_workspace/SET_statusNetworkCoreStatusProgressClear');
      this.$store.dispatch('mod_workspace/SET_elementUnselect');
      this.$store.dispatch('mod_workspace/SET_openTest', true);
      this.tutorialPointActivate({way: 'next', validation: 'tutorial_run-test-button'})
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
    trainingTargetMetric() {

      if (this.popupInfo.acc_train) {
        return `Training Accuracy: ${ this.popupInfo.acc_train.toFixed(2).replace('.00', '') }%`;
      }
      
      if (this.popupInfo.r_sq_train) {
        return `Training R Squared:  ${ this.popupInfo.r_sq_train.toFixed(2).replace('.00', '') }%`;
      }

      return '';
    },
    validationTargetMetric() {

      if (this.popupInfo.acc_val) {
        return `Validation Accuracy: ${ this.popupInfo.acc_val.toFixed(2).replace('.00', '') }%`;
      }
      
      if (this.popupInfo.r_sq_val) {
        return `Validation R Squared:  ${ this.popupInfo.r_sq_val.toFixed(2).replace('.00', '') }%`;
      }

      return '';
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
    span {
      display: block;
    }
    .results-info--validation {
      margin-right: 1rem;
    }
  }
</style>
