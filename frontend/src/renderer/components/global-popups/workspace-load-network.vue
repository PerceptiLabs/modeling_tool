<template lang="pug">
  base-global-popup(
    :title="popupTitle"
    title-align="text-center"
    @closePopup="closePopup"
    )
    template(:slot="popupTitle + '-content'")
      .settings-layer_section.mb-footer
        .form_row
          .form_label Load settings:
          .form_input
            base-radio(group-name="group" :value-input="false" v-model="isLoadTrainedModel")
              span Load model only
            base-radio(group-name="group" :value-input="true" v-model="isLoadTrainedModel")
              span Load trained model

    template(slot="action")
      button.btn.btn--secondary(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="ok") Continue


</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";

export default {
  name: "WorkspaceLoadNetwork",
  components: {BaseGlobalPopup},
  data() {
    return {
      popupTitle: 'Choose what to load',
      isLoadTrainedModel: true
    }
  },
  computed: {
    okAction() {
      return this.$store.state.globalView.popupConfirmOk
    }
  },
  methods: {
    closePopup() {      
      this.$store.commit('globalView/set_loadSettingPopup', {
        visible: false,
        ok: null
      });
    },
    ok() {
      this.okAction(this.isLoadTrainedModel);
      this.closePopup();
    },
   }
}
</script>

<style lang="scss" scoped>

</style>
