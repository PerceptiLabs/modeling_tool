<template lang="pug">
  chart-spinner(v-if="loadingMessage" :text="loadingMessage")
  main.export-wrapper(v-else)
    h1.export-header Export
    div.padded-box
      h1.section-title.mb-20 1. Select Trained Models
      ul.reset-list-style
        li.model-list.model-list-header
          div.w-170
            span File name
          div.w-130
            span Accuracy
          div.w-130
            span Loss
          div.w-130
            span Runtime
        li.model-list(v-for="model in trainedModels")
          div.w-170
            base-checkbox(
              @input="handleModelSelect($event, model.networkID)"
              :styleTypeSecondary="true"
              :value="model.isChecked"
              ).export-checkbox
                | {{model.networkName}}
          div.w-130
            span -
          div.w-130
            span -
          div.w-130
            span {{ model && model.networkMeta && model.networkMeta.coreStatus && model.networkMeta.coreStatus.Training_Duration ? model.networkMeta.coreStatus.Training_Duration.toFixed(2) + 's' : '-' }}
    div.padded-box
      .export-settings-wrapper
        h1.section-title 2. Choose Export Settings
        .settings-layer_section
          .form_holder.d-flex.align-items-center
            .form_label.export-label Save to:
            .form_row
              input.form_input.export-input(type="text" v-model="settings.Location" readonly)
              button.btn.btn--dark-blue-rev.btn-medium(type="button" @click="saveLoadFile") Browse
          div.d-flex
            div
              h1 Format
              .form_holder
                base-radio(:styleTypeSecondary="true" group-name="resizeAutomaticType" value-input="TFModel" v-model="settings.Type")
                  span TensorFlow Model
                base-radio(:styleTypeSecondary="true" group-name="resizeAutomaticType" value-input="ipynb" v-model="settings.Type")
                  span Jupyter Notebook
            div.w-120
              template(v-if="settings.Type === 'TFModel'")
                h1 Compress
                .form_holder
                  span.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a frozen model (.pb) which\ncan be used for inference`")
                    base-checkbox(:styleTypeSecondary="true" v-model="settings.Compressed") Compressed
                .form_holder(v-if="settings.Type === 'TFModel'")
                  span.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a quantized tf-lite model which\ncan be used for edge devices`")
                    base-checkbox(:styleTypeSecondary="true" v-model="settings.Quantized")  Quantized
    button.btn.btn--primary.btn-medium(
      type="button"
      @click="exportModels"
      style="margin: 30px"
    ) Export
</template>

<script>
import { mapState, mapGetters } from "vuex";
import { doesFileExist as rygg_doesFileExist } from '@/core/apiRygg';
import ChartSpinner from '@/components/charts/chart-spinner';

export default {
  name: 'ExportPage',
  components: {
    ChartSpinner,
  },
  created() {
    this.filterTrainedModels();
  },
  data() {
    return {
      trainedModels: [],
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
      },
      loadingMessage: '',
    };
  },
  mounted() {
  },
  computed: {
    ...mapGetters({
      testStatus: 'mod_test/GET_testStatus',
      models:     'mod_workspace/GET_models',
    }),
    ...mapState({
      isTestConfigurationPopupOpened: state =>
        state.globalView.globalPopup.showTestConfigurationPopup
    }),
    checkedModelsLength() {
      return this.trainedModels && this.trainedModels.filter(m => m.isChecked).length;
    },
    isAllModelsChecked() {
      const trainedModelsLength = this.trainedModels.length;
      console.log({
        trainedModelsLength,
        checkedModelsLength: this.checkedModelsLength,
      });
      return trainedModelsLength ===  this.checkedModelsLength;
    }
  },
  watch: {
    'models'() {
      this.filterTrainedModels();
    },
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
    isModelTrained() {
      return this.$store.dispatch('mod_api/API_checkTrainedNetwork')
    },
    filterTrainedModels() {
      if(!this.models.length) {
        this.trainedModels = [];
      }
      const promises = this.models.map(m => this.$store.dispatch('mod_api/API_checkTrainedNetwork', m.networkID))
      Promise.allSettled(promises)
        .then(results => {
          const tempArrayWithTrainedModels = [];
          results.map(res => {
            if(res.value.result.content) {
              tempArrayWithTrainedModels.push(parseInt(res.value.receiver, 10))
            }
          })

          let filteredModels = this.models.filter(model => {
            return tempArrayWithTrainedModels.some(id => model.networkID === id);
          })
          filteredModels = filteredModels.map(m => {
            this.$set(m, 'isChecked', false);
            return m;
          })
          this.trainedModels = filteredModels;
        });
    },
    async exportModels() {
      const selectedModels = this.trainedModels.filter(m => m.isChecked);
      if(selectedModels.length === 0) {
        return;
      }
      try {
        for(const model of selectedModels) {
          this.loadingMessage = `Exporting model: ${model.networkName}..`;
          const theSettings = {...this.settings};
          theSettings.modelId = model.networkID;
          theSettings.name = model.networkName;
          if(this.settings.Location !== '' && this.settings.Type === 'ipynb') {
            const fileName = this.settings.Location + `/${model.networkName}.ipynb`;
            const doesFileExist = await rygg_doesFileExist(fileName);

            if(doesFileExist) {
              await this.$store.dispatch('globalView/GP_confirmPopup', {
                text: `That file '${fileName}' already exists. Are you sure you want to overwrite it?`,
                ok: async () => {
                  await exportData.call(this, theSettings)
                }
              })
            } else {
              await exportData.call(this, theSettings)
            }
          } else {
            await exportData.call(this, theSettings)
          }
        }
        this.$store.dispatch('globalView/GP_infoPopup', "Exported with success.", {root: true});
      } catch (e) {
        this.$store.dispatch('globalView/GP_errorPopup', "Something went wrong.", {root: true});
        this.loadingMessage = ``;
      }
      
      this.loadingMessage = ``;
      
      
      async function exportData(settings = null) {
        await this.$store.dispatch('mod_api/API_exportData', settings);
      }
     
    },
    setExportPath(value) {
      if (value && Array.isArray(value) && value.length > 0) {
        this.settings.Location = value[0];
      }
      this.$store.dispatch('globalView/SET_filePickerPopup', false);
    },
    saveLoadFile() {
      this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.setExportPath});
    },
    handleModelSelect(isChecked, modelId) {
      let modelIndex = null;
      for(let i = 0; i < this.trainedModels.length; i++) {
        this.$set(this.trainedModels[i], 'isChecked', false);
        if(modelId === this.trainedModels[i].networkID) {
          modelIndex = i;
        }
      }
      
      if(isChecked) {
        this.$set(this.trainedModels[modelIndex], 'isChecked', true);
      }
      
    }
  }
};
</script>

<style lang="scss" scoped>
.export-label {
  margin-right: 30px;
  font-size: 14px;
  font-family: Roboto, sans-serif;
}
.export-input {
  background-color: #202532;
  text-align: left;
  border: 1px solid #5E6F9F;
  height: 36px;
  width: 100%;
}
.btn-medium {
  height: 35px;
  font-family: Nunito Sans, sans-serif;
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
}
.export-wrapper {
  height: 100%;
  background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
  border: 1px solid rgba(97, 133, 238, 0.4);
  box-sizing: border-box;
}
.export-header {
  padding: 12px 20px;
  border-bottom: 1px solid #b6c7fb;
}
.padded-box {
  padding: 20px 30px 45px;
  border-bottom: 1px solid rgba(#b6c7fb, .5);
}
.section-title {
  font-family: Roboto, sans-serif;
  font-weight: 500;
  font-size: 14px;
  line-height: 16px;
  letter-spacing: 0.02em;
  color: #fff;
}
.w-130{
  width: 130px;
}
.w-170 {
  width: 170px;
}
.reset-list-style {
  padding-left: 0;
  list-style-type: none;
}
.export-checkbox {
  width: 170px;
    font-size: 20px;
    font-family: Roboto, sans-serif;
}
.model-list {
  display: flex;
  margin-bottom: 22px;
  font-size: 14px;
  font-family: Roboto, sans-serif;
}
.line-separator {
  border-bottom: 1px solid rgba(#b6c7fb, .5);
}
.export-settings-wrapper {
  max-width: 320px;
}
.w-120 {
  min-width: 120px;
}
.mb-20 {
  margin-bottom: 20px;
}
</style>
