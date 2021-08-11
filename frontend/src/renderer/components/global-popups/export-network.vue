<template lang="pug">
  base-global-popup(:tab-set="popupTitle" @closePopup="closePopup")
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
          span.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a frozen model (.pb) which\ncan be used for inference`")
            base-checkbox(v-model="settings.Compressed") Compressed
        .form_holder(v-if="settings.Type === 'TFModel'")
          span.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a quantized tf-lite model which\ncan be used for edge devices`")
            base-checkbox(v-model="settings.Quantized")  Quantized

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="ok") Export


</template>

<script>
import { isWeb } from "@/core/helpers";
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
import { doesFileExist as rygg_doesFileExist } from '@/core/apiRygg';

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
        Quantized: false,
        name: '',
        modelId: null,
      }
    }
  },
  mounted() {
    this.settings.name = this.$store.getters['mod_workspace/GET_currentNetwork'].networkName;
    this.settings.modelId = this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
  },
  watch: {
    'settings.Quantized'(value) {
      if(value) {
        this.settings.Compressed = false;
      }
    },
    'settings.Compressed'(value) {
      if(value) {
        this.settings.Quantized = false;
      }
    },
  },
  methods: {
    setExportPath(value) {
      if (value && Array.isArray(value) && value.length > 0) {
        this.settings.Location = value[0];
      }
      this.$store.dispatch('globalView/SET_filePickerPopup', false);
    },
    saveLoadFile() {
      this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.setExportPath});
    },
    closePopup() {
      this.$store.commit('globalView/set_exportNetworkPopup', false);
    },
    async ok() {
      if(this.settings.Location !== '' && this.settings.Type === 'ipynb') {
        const fileName = this.settings.Location + `/${this.settings.name}.ipynb`;
        const doesFileExist = await rygg_doesFileExist(fileName);
       
       if(doesFileExist) {
          this.$store.dispatch('globalView/GP_confirmPopup', {
            text: 'That file already exists. Are you sure you want to overwrite it?',
            ok: async () => {
              await exportData.call(this, this.settings)
            }
          })
        } else {
          await exportData.call(this, this.settings)
        }
      } else {
        await exportData.call(this, this.settings)
      }

      async function exportData(settings = null) {
        this.closePopup();
        let exportType = this.getSettingExportType(this.settings);

        const payload = {
          name: this.settings.name,
          Location: this.settings.Location,
          modelId: this.settings.modelId,
          Type: exportType,
        };
        await this.$store.dispatch('mod_api/API_exportData', payload);
        this.$store.dispatch('globalView/GP_infoPopup', 'Exported with success.')
        
      }
    },
    getSettingExportType(settings) {
      if(settings.Type === 'ipynb') {
        return settings.Type;
      }
      
      let exportType = 'Standard';
      if(settings.Compressed) {
        exportType = 'Compressed';
      } else if(settings.Quantized) {
        exportType = 'Quantized';
      }
      
      return exportType;
    }
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
.checkbox-tooltip {
  display: inline-block;
}
</style>
