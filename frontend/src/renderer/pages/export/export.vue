<template lang="pug">
  chart-spinner(v-if="loadingMessage" :text="loadingMessage")
  main.export-wrapper(v-else)
    perfect-scrollbar
      h1.export-header.bold Export
      .export-view
        .section-select-model
          .section-title
            .step 1.
            .middle-text.bold Select trained models        
          .section-content
            table.trained-model-table
              tr.bold
                th
                  //- base-checkbox(v-if="trainedModels.length > 0" :value="isAllModelsChecked" :onClick="toggleSelectAll" )
                th File name
                th Accuracy
                th Loss
                th Runtime
              tr(v-for="(model, index) in trainedModels" :key="model.networkID")
                td
                  base-checkbox(
                    @input="handleModelSelect($event, model.networkID)"
                    :value="model.isChecked"
                  )
                td {{model.networkName}}
                td -
                td -
                td 
                  span {{ model && model.networkMeta && model.networkMeta.coreStatus && model.networkMeta.coreStatus.Training_Duration ? model.networkMeta.coreStatus.Training_Duration.toFixed(2) + 's' : '-' }}

        .divider

        .section-settings  
          .section-title
            .step 2.
            .middle-text.bold Choose Export Settings
          .section-content
            table.settings-table
              tr
                td.bold.right Save to:
                td.input_group.form_row(colSpan="2")
                  input.form_input(type="text" v-model="settings.Location" readonly)
                  button.btn.btn--primary(
                    type="button"
                    @click="saveLoadFile"
                    :class="{'flash-button': !wasSavePathChoosen}"
                  ) Browse
              tr
                td.bold.right Format
                td
                  base-radio.mb-5(group-name="formatTypeGroup" value-input="TFModel" v-model="settings.Type")
                    span TensorFlow Model
                  base-radio.mb-5(group-name="formatTypeGroup" value-input="ipynb" v-model="settings.Type")
                    span Jupyter Notebook

                  
                  template(v-if="isServingEnabled")
                    base-radio(:styleTypeSecondary="true" group-name="resizeAutomaticType" value-input="FastAPI" v-model="settings.Type")
                      span FastAPI Server
                    base-radio(:styleTypeSecondary="true" group-name="resizeAutomaticType" value-input="Serve Gradio" v-model="settings.Type")
                      span Serve Gradio
              tr(v-if="settings.Type === 'TFModel'")
                td.bold.right Compress
                td
                  span.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a frozen model (.pb) which\ncan be used for inference`")
                    base-checkbox(v-model="settings.Compressed") Compressed
                td
                  span.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a quantized tf-lite model which\ncan be used for edge devices`")
                    base-checkbox(v-model="settings.Quantized")  Quantized

        .divider

        button.btn.btn--primary(type="button"
          @click="exportModels") Export
</template>

<script>
import ChartSpinner from '@/components/charts/chart-spinner';
import { mapState, mapGetters } from "vuex";
import { isModelTrained } from '@/core/modelHelpers';
import { isServingEnabled } from '@/core/helpers.js';

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
        { text: 'Jupyter Notebook',         value: 'ipynb'},
        { text: 'FastAPI Server',           value: 'FastAPI' },
        { text: 'Serve Gradio',             value: 'Serve Gradio' }
      ],
      settings: {
        Location: '',
        Type: 'TFModel',
        Compressed: false,
        Quantized: false,
        name: '',
      },
      loadingMessage: '',
      wasSavePathChoosen: false,
    };
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
      return trainedModelsLength ===  this.checkedModelsLength;
    },
    isServingEnabled() {
      return isServingEnabled();
    }
  },
  methods: {    
    isModelTrained() {
      return this.$store.dispatch('mod_api/API_checkTrainedNetwork')
    },
    filterTrainedModels() {
      if(!this.models.length) {
        this.trainedModels = [];
      }
      this.trainedModels = this.models.filter((model) => isModelTrained(model));
    },
    async exportModels() {
      const selectedModels = this.trainedModels.filter(m => m.isChecked);
      if(selectedModels.length === 0) {
        this.$store.dispatch('globalView/GP_infoPopup', "Select model to export.", {root: true});
        return;
      }
      
      if(!this.wasSavePathChoosen) { 
        this.$store.dispatch('globalView/GP_infoPopup', "Chose where to save the model.", {root: true});
        return;
      }
      try {
        let retMessage = '';
        for(const model of selectedModels) {
          this.loadingMessage = `Exporting model: ${model.networkName}..`;
          const theSettings = {...this.settings};
          theSettings.modelId = model.networkID;
          theSettings.name = model.networkName;
          retMessage = await exportData.call(this, theSettings);
        }
        this.$store.dispatch('globalView/GP_infoPopup', retMessage , {root: true});
      } catch (e) {
        this.$store.dispatch('globalView/GP_errorPopup', "Something went wrong.", {root: true});
        this.loadingMessage = ``;
      }
      this.loadingMessage = ``;
      async function exportData(settings = null) {
       return await this.$store.dispatch('mod_api/API_exportData', settings);
      }
    },
    setExportPath(value) {
      if (value && Array.isArray(value) && value.length > 0) {
        this.settings.Location = value[0];
        this.wasSavePathChoosen = true;
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
    },
    toggleSelectAll() {
      if(this.isAllModelsChecked) {
        for(let i = 0; i < this.trainedModels.length; i++) {
          this.$set(this.trainedModels[i], 'isChecked', false);
        }
      } else {
        for(let i = 0; i < this.trainedModels.length; i++) {
          this.$set(this.trainedModels[i], 'isChecked', true);
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>

@keyframes clickMeFrame {
  0% {
    box-shadow: 0 0 3px #6185EE;
  }
  50% {
    box-shadow: 0 0 10px #6185EE;
  }
  100% {
    box-shadow: 0 0 3px #6185EE;
  }
}
.flash-button {
  animation-name: clickMeFrame;
  animation-duration: 1.3s;
  animation-iteration-count: infinite;
}

.export-header {
  margin-bottom: 10px;
}
.export-wrapper {
  background-color: theme-var($neutral-7);
  border-radius: 15px 0px 0px 0px;
  padding: 10px 20px;
  display: flex;
  flex-direction: column;
}
.export-view {
  background: theme-var($neutral-8);
  border: $border-1;
  box-sizing: border-box;
  border-radius: 4px;

  padding: 45px 30px;
  flex: 1;
  position: relative;

  .divider {
    border-bottom: $border-1;
    margin: 35px 0px;
  }
}

.checkbox-tooltip {
  display: inline-block;
}

.section-title {
  display: flex;
  align-items: center;
  margin-bottom: 25px;

  & .step {
    width: 42px;
    height: 42px;
    background: #D9E2FF;

    font-weight: bold;
    font-size: 20px;
    line-height: 23px;
    display: flex;
    justify-content: center;
    align-items: center;

    color: $color-6;
    border-radius: 50%;

    margin-right: 15px;    
  }
}
.section-content {
  margin-left: 57px;
}
table {
  font-size: 14px;
  td, th {
    padding-right: 20px;
  }
  tr:not(:last-child) {
    td, th {
      padding-bottom: 30px;
    }
  }
}
.settings-table {
  .right {
    text-align: right;
  }
}
</style>
