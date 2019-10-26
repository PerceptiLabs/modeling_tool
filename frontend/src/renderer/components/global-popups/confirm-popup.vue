<template lang="pug">
  .popup-global(v-if="isShowPopup")
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        //.popup_header.active
      .popup_body
        .settings-layer_section
          .section_attention !
          p.section_text.middle-text.text-center {{infoPopup}}
      .popup_foot
        button.btn-info-popup(type="button"
          @click="ok") Ok
        button.btn-info-popup(type="button"
          @click="cancel") Cancel

</template>

<script>
  export default {
    name: "confirmPopup",
    computed: {
      infoPopup() {
        return this.$store.state.globalView.globalPopup.showConfirmPopup
      },
      cancelAction() {
        return this.$store.state.globalView.popupConfirmCancel
      },
      okAction() {
        return this.$store.state.globalView.popupConfirmOk
      },
      isShowPopup() {
        return this.infoPopup.length
      },
    },
    methods: {
      ok() {
        this.okAction();
        this.closePopup();
      },
      cancel() {
        this.cancelAction ? this.cancelAction() : null;
        this.closePopup();
      },
      closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../scss/base";
  @import "../../scss/common/info-popup";
</style>
