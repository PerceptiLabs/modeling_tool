<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header.active
          h3 Result
      .popup_body
        .settings-layer_section

        //- .body_results-info
        //-   .results-info--validation
        //-     p Validation
        //-     span Validation Accuracy: 70.86%
        //-     span Validation Loss: 2.35
        //-   .results-info--validation
        //-       p Training
        //-       span Training Accuracy: 71.35%
        //-       span Training Loss: 2.28  

      .popup_foot
        button.btn.btn--primary(type="button"
          @click="closePopup()") Cancel
        button.btn.btn--primary(type="button"
          id="tutorial_run-test-button"
          @click="runTest()") Run test
</template>

<script>
import { mapActions } from 'vuex';
export default {
  name: "GeneralResult",
  mounted() {
    this.tutorialPointActivate({way: 'next', validation: 'tutorial_statistic-tab'})
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
    }
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
