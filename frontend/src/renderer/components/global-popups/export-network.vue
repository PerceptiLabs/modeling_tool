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
        .form_holder(v-if="settings.Type === 'ipynb'")
          .form_label Name:
          .form_row
            input.form_input(type="text" v-model="settings.name")
        .form_holder(v-if="settings.Type === 'TFModel'")
          base-checkbox(v-model="settings.Compressed") Compressed

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="ok") Export


</template>

<script>
import { isWeb } from "@/core/helpers";
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
import { doesFileExist as fileserver_doesFileExist } from '@/core/apiFileserver';

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
        name: '',
      }
    }
  },
  mounted() {
    this.settings.name = this.$store.getters['mod_workspace/GET_currentNetwork'].networkName;
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
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
    async ok() {
      if(this.settings.Location !== '') {
        const fileName = this.settings.Location + `/${this.settings.name}.ipynb`;
        const isFolderAlreadyExist = await fileserver_doesFileExist(fileName);
       
       if(isFolderAlreadyExist) {
          this.$store.dispatch('globalView/GP_confirmPopup', {
            text: 'That file already exists. Are you sure you want to overwrite it?',
            ok: () => {
              exportData.call(this, this.settings)
            }
          })
        } else {
          exportData.call(this, this.settings)
        }
      } else {
        exportData.call(this, this.settings)
      }

      function exportData(settings = null) {
        this.$store.dispatch('mod_api/API_exportData', this.settings);
        this.closePopup();
      }
    },
   }
}
</script>

<style lang="scss" scoped>

.popup-button {
  width: 9.5rem;
  height: 3.5rem;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 22px;
}
</style>
