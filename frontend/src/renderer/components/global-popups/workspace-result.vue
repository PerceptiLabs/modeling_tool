<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup.popup-small
      .popup-background
        h1.popup-title.bold(class="text-center") Result
        
        .popup_body
          .settings-layer_section
            .chart-spinner-wrapper(v-if="isLoading")
              chart-spinner
            .body_results-info.d-flex(v-else)
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
            @click="gotToTestPage") Go To Test
          
</template>

<script>
import { mapState } from 'vuex';
import ChartSpinner     from '@/components/charts/chart-spinner'

export default {
  name: "GeneralResult",
  components: { ChartSpinner },
  mounted() {
    this.$store.dispatch('mod_api/API_getResultInfo')
      .then((data)=> {

        // TOREMOVE
        delete data['consoleLogs']
        this.popupInfo = {...data};
      }).finally(()=> { this.isLoading = false });
  },
  data() {
    return {
      popupInfo: {},
      isLoading: true,
    }
  },
  methods: {
    gotToTestPage(){
      this.$router.push({name: 'test'});
      this.$store.commit('globalView/GP_showNetResult', false);
    },
    closePopup() {
      this.$store.commit('globalView/GP_showNetResult', false);
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
  .chart-spinner-wrapper {
    position: relative;
    min-height: 100px;
    .chart-spinner-box {
      background: transparent;
    }
  }
</style>
