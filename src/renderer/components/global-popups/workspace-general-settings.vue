<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closeGlobalSet()")
    section.popup
      .popup_tab-set
        .popup_header.active
          h3 General Settings
      .popup_body
        .settings-layer_section
          .form_row
            .form_label Data partition:
            .form_input
              label.form_row
                .form_label Sigmoid
                .form_input
                  input(type="number" v-model="settings.dataSigmoid")
                  span &nbsp; %
              label.form_row
                .form_label Validation
                .form_input
                  input(type="number" v-model="settings.dataValidation")
                  span &nbsp; %
              label.form_row
                .form_label Test
                .form_input
                  input(type="number" v-model="settings.dataTest")
                  span &nbsp; %
        .settings-layer_section
          label.form_row
            .form_label Batch size:
            .form_input
              input(type="number" v-model="settings.batchSize")
        .settings-layer_section
          .form_row
            .form_label Shuffle data:
            .form_input
              base-radio(groupName="group2" :valueInput="true" v-model="settings.shuffleData")
                span Yes
              base-radio(groupName="group2" :valueInput="false" v-model="settings.shuffleData")
                span No
        .settings-layer_section
          label.form_row
            .form_label Epochs:
            .form_input
              input(type="number" v-model="settings.epochs")
        .settings-layer_section
          .form_row
            .form_label Dropout rate:
            .form_input
              input(type="number" v-model="settings.dropoutRate")
        .settings-layer_section
          label.form_row
            .form_label Save model every:
            .form_input
              input(type="number" v-model="settings.saveModel")
              span &nbsp; epoch
      .popup_foot
        button.btn.btn--primary(type="button"
          @click="setGlobalSet()") Apply

</template>

<script>
export default {
  name: "GeneralSettings",
  data() {
    return {
      settings: {
        isEmpty: false,
        dataSigmoid: null,
        dataValidation: null,
        dataTest: null,
        batchSize: null,
        shuffleData: null,
        epochs: null,
        dropoutRate: null,
        saveModel: null,
      }
    }
  },
  computed: {

  },
  methods: {
    setGlobalSet() {
      for (var set in this.settings) {
        if (this.settings[set] === null) {
          return
        }
      }
      this.$store.commit('mod_workspace/SET_networkSettings', this.settings);
      this.closeGlobalSet();
      this.$store.commit('globalView/SET_showCoreSideSettings', true);
    },
    closeGlobalSet() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
