<template lang="pug">
  base-global-popup(
    :tab-set="popupTitle"
    )
    template(slot="Choose what to load-content")
      .settings-layer_section
        .form_row
          .form_label Load settings:
          .form_input
            base-radio(group-name="group" :value-input="false" v-model="isLoadTrainedModel")
              span Load model only
            base-radio(group-name="group" :value-input="true" v-model="isLoadTrainedModel")
              span Load trained model

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="answerPopup") Continue


</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";

export default {
  name: "WorkspaceLoadNetwork",
  components: {BaseGlobalPopup},
  data() {
    return {
      popupTitle: ['Choose what to load'],
      promiseOk: null,
      promiseFail: null,
      isLoadTrainedModel: true
    }
  },
  methods: {
    openPopup() {
      return new Promise((resolve, reject) => {
        this.promiseOk = resolve;
        this.promiseFail = reject;
      });
    },
    closePopup() {
      this.promiseFail(false)
    },
    answerPopup() {
      this.promiseOk(this.isLoadTrainedModel);
    },
   }
}
</script>

<style lang="scss" scoped>

</style>
