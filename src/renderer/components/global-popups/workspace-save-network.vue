<template lang="pug">
  base-global-popup(
    v-if="isShow"
    :tab-set="popupTitle"
    )
    template(slot="Choose what to save-content")
      .settings-layer_section
        .form_row
          .form_input
            base-radio(group-name="group" :value-input="false" v-model="isSaveTrainedModel")
              span Save only model
            base-radio(group-name="group" :value-input="true" v-model="isSaveTrainedModel")
              span Save trained network
              //-Cross-Entropy

    template(slot="action")
      button.btn.btn--primary(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="answerPopup") Continue


</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";

export default {
  name: "WorkspaceSaveNetwork",
  components: {BaseGlobalPopup},
  data() {
    return {
      isShow: false,
      popupTitle: ['Choose what to save'],
      isSaveTrainedModel: true,
      promiseOk: null,
      promiseFail: null,
    }
  },
  methods: {
    openPopup() {
      this.isShow = true;
      return new Promise((resolve, reject) => {
        this.promiseOk = resolve;
        this.promiseFail = reject;
      });
    },
    closePopup() {
      this.isShow = false;
      this.promiseFail()
    },
    answerPopup() {
      this.isShow = false;
      this.promiseOk(this.isSaveTrainedModel);
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
