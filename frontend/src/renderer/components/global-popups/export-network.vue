<template lang="pug">
  base-global-popup(:tab-set="popupTitle")
    template(slot="Export-content")
      .settings-layer_section
        .form_holder
          .form_label Path:
          .form_row
            input.form_input(type="text" v-model="settings.Location" readonly)
            button.btn.btn--dark-blue-rev(type="button" @click="saveLoadFile") Browse
        .form_holder
          .form_label Export as:
          .form_row
            base-select(
              v-model="settings.Type"
              :select-options="selectOptions"
            )
        .form_holder
          base-checkbox(v-model="settings.Compressed") Compressed

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="ok") Export


</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";

export default {
  name: "ExportNetwork",
  components: {BaseGlobalPopup},
  data() {
    return {
      popupTitle: ['Export'],
      selectOptions: [
        { text: 'TensorFlow Model',         value: 'TFModel' },
        { text: 'Jupyter Notebook (ipynb)', value: 'ipynb' }
      ],
      settings: {
        Location: '',
        Type: 'TFModel',
        Compressed: false,
      }
    }
  },
  methods: {
    setExportPath(value) {
      if (value && Array.isArray(value) && value.length > 0) {
        this.settings.Location = value[0];
      }
      this.$store.dispatch('globalView/SET_filePickerPopup', false);
    },
    saveLoadFile() {
      if(isWeb()) {
        this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.setExportPath});
      } else {
        loadPathFolder()
          .then((pathArr)=> this.settings.Location = pathArr[0] )
          .catch((err)=> console.error(err) ) 
      }
    },
    exportData() {
      this.$store.dispatch('mod_api/API_exportData', this.settings);
    },  
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
    ok() {
      this.closePopup();
    },
   }
}
</script>

<style lang="scss" scoped>

</style>
