<template lang="pug">
  .popup-global(v-if="isShowPopup")
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup-new-ui-header
        .popup-new-ui-header-text Delete Models
        svg.popup-new-ui-header-close-icon(@click="cancel" width="8" height="8" viewBox="0 0 8 8" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(fill-rule="evenodd" clip-rule="evenodd" d="M0.227694 0.227694C0.279946 0.175311 0.342018 0.13375 0.410356 0.105392C0.478695 0.0770351 0.551956 0.062439 0.625944 0.062439C0.699932 0.062439 0.773194 0.0770351 0.841532 0.105392C0.90987 0.13375 0.971943 0.175311 1.02419 0.227694L4.00094 3.20557L6.97769 0.227694C7.02999 0.175395 7.09208 0.133909 7.16041 0.105605C7.22874 0.0773014 7.30198 0.0627335 7.37594 0.0627335C7.44991 0.0627335 7.52314 0.0773014 7.59148 0.105605C7.65981 0.133909 7.7219 0.175395 7.77419 0.227694C7.82649 0.279993 7.86798 0.342081 7.89628 0.410413C7.92459 0.478745 7.93915 0.551982 7.93915 0.625944C7.93915 0.699906 7.92459 0.773144 7.89628 0.841476C7.86798 0.909808 7.82649 0.971895 7.77419 1.02419L4.79632 4.00094L7.77419 6.97769C7.82649 7.02999 7.86798 7.09208 7.89628 7.16041C7.92459 7.22874 7.93915 7.30198 7.93915 7.37594C7.93915 7.44991 7.92459 7.52314 7.89628 7.59148C7.86798 7.65981 7.82649 7.7219 7.77419 7.77419C7.7219 7.82649 7.65981 7.86798 7.59148 7.89628C7.52314 7.92459 7.44991 7.93915 7.37594 7.93915C7.30198 7.93915 7.22874 7.92459 7.16041 7.89628C7.09208 7.86798 7.02999 7.82649 6.97769 7.77419L4.00094 4.79632L1.02419 7.77419C0.971895 7.82649 0.909808 7.86798 0.841476 7.89628C0.773144 7.92459 0.699906 7.93915 0.625944 7.93915C0.551982 7.93915 0.478745 7.92459 0.410413 7.89628C0.342081 7.86798 0.279993 7.82649 0.227694 7.77419C0.175395 7.7219 0.133909 7.65981 0.105605 7.59148C0.0773014 7.52314 0.0627335 7.44991 0.0627335 7.37594C0.0627335 7.30198 0.0773014 7.22874 0.105605 7.16041C0.133909 7.09208 0.175395 7.02999 0.227694 6.97769L3.20557 4.00094L0.227694 1.02419C0.175311 0.971943 0.13375 0.90987 0.105392 0.841532C0.0770351 0.773194 0.062439 0.699932 0.062439 0.625944C0.062439 0.551956 0.0770351 0.478695 0.105392 0.410356C0.13375 0.342018 0.175311 0.279946 0.227694 0.227694Z" fill="#B6C7FB")
      .popup_tab-set
        //.popup_header.active
      .popup_body
          p.message This action cannot be undone. <br/> Are you sure you want to continue?
          .d-flex.align-items-center(style="padding: 0 30px 15px 30px")
            base-checkbox.is-silver.w-100(v-model="dontShowThisAgain" :isNewUi="true")
              span.dont-show-text(style="color: #C4C4C4;") Do not show this again

      .popup_foot
        button.btn-info-popup.dark(type="button"
          @click="cancel") Cancel
        button.btn-info-popup(type="button"
          @click="ok") Delete

</template>

<script>
  import { LOCAL_STORAGE_HIDE_DELETE_MODAL } from '@/core/constants.js'
  export default {
    name: "deleteConfirmPopup",
    data() {
      return {
        dontShowThisAgain: false,
      }
    },
    computed: {

      cancelAction() {
        return this.$store.state.globalView.popupConfirmCancel
      },
      okAction() {
        return this.$store.state.globalView.popupConfirmOk
      },
      isShowPopup() {
        return this.$store.state.globalView.globalPopup.showDeleteConfirmPopup;
      },
    },
    methods: {
      ok() {
        this.okAction();
        if (this.dontShowThisAgain) {
          localStorage.setItem(LOCAL_STORAGE_HIDE_DELETE_MODAL, true);
        }
        this.closePopup();
      },
      cancel() {
        this.cancelAction ? this.cancelAction() : null;
        this.closePopup();
      },
      closePopup() {
        this.$store.commit('globalView/gp_deleteConfirmPopup', {
          show: false,
          ok: null,
          cancel: null
        });
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../scss/base";
  @import "../../scss/common/info-popup";

  p.message {
    color: white;
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: 12px;
    line-height: 16px;    
    padding: 20px 30px 0px 30px;
  }
</style>
