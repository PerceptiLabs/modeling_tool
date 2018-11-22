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
                .form_label Training
                .form_input
                  input(type="number" v-model="settings.Data_partition.Training")
                  span &nbsp; %
              label.form_row
                .form_label Validation
                .form_input
                  input(type="number" v-model="settings.Data_partition.Validation")
                  span &nbsp; %
              label.form_row
                .form_label Test
                .form_input
                  input(type="number" v-model="settings.Data_partition.Test")
                  span &nbsp; %
        .settings-layer_section
          label.form_row
            .form_label Batch size:
            .form_input
              input(type="number" v-model="settings.Batch_size")
        .settings-layer_section
          .form_row
            .form_label Shuffle data:
            .form_input
              base-radio(groupName="group2" :valueInput="true" v-model="settings.Shuffle_data")
                span Yes
              base-radio(groupName="group2" :valueInput="false" v-model="settings.Shuffle_data")
                span No
        .settings-layer_section
          label.form_row
            .form_label Epochs:
            .form_input
              input(type="number" v-model="settings.Epochs")
        .settings-layer_section
          .form_row
            .form_label Dropout rate:
            .form_input
              input(type="number" v-model="settings.Dropout_rate")
        .settings-layer_section
          label.form_row
            .form_label Save model every:
            .form_input
              input(type="number" v-model="settings.Save_model_every")
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
        Epochs: "1",
        Batch_size: "32",
        Data_partition: {
          Training: "70",
          Validation: "20",
          Test: "10"
        },
        Dropout_rate: "0.5",
        Shuffle_data: true,
        Save_model_every: "1"
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
