<template lang="pug">
  base-global-popup(
    :title="popupTitle"
    title-align="text-center"
    v-if="isShowPopup"
    size="small"
    @closePopup="closePopup"
  )
    template(:slot="popupTitle + '-content'")
      .w-250.mb-footer
        .form_row.mt-4
          label.form_label.bold Type "delete"
        .form_row
          input.form_input.w-200(type="text" v-model="textDelete")
        //- p.message This action cannot be undone. <br/> Are you sure you want to continue?
        .d-flex.align-items-center.mt-4
          base-checkbox.w-100(v-model="dontShowThisAgain")
            span.dont-show-text Do not show this again

    template(slot="action")
      button.btn.btn--secondary(type="button"
        @click="cancel") Cancel
      button.btn.btn--danger(type="button" :disabled="!deleteConfirmed"
        @click="ok") Delete

</template>

<script>
  import BaseGlobalPopup                  from "@/components/global-popups/base-global-popup";
  import { LOCAL_STORAGE_HIDE_DELETE_MODAL } from '@/core/constants.js'

  export default {
    name: "deleteConfirmPopup",
    components: { BaseGlobalPopup },
    data() {
      return {
        popupTitle: 'Are you sure you want to delete this?',
        dontShowThisAgain: false,
        textDelete: '',
      }
    },
    computed: {
      deleteConfirmed() {
        return this.textDelete.toLowerCase() === 'delete'
      },
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
        this.textDelete = '';
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
  
  @import "../../scss/common/info-popup";

  p.message {
    font-style: normal;
    font-weight: normal;
    font-size: 14px;
    line-height: 16px;    
    padding: 20px 30px 0px 30px;
  }
  .w-250 {
    width: 250px;
    margin-left: auto;
    margin-right: auto;
  }
  .form_label {
    font-size: 16px;
  }
  .mt-4 {
    margin-top: 20px;
  }
</style>
