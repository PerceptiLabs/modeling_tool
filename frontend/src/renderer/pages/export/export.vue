<template lang="pug">
  chart-spinner(v-if="loadingMessage" :text="loadingMessage")
  div(v-else)
    h1.export-header.bold Export
    div.export-page-wrapper
      .export-model-list.export-view
      
        .section-select-model
          .section-title
            .middle-text 1. Select trained models
          .divider
          div.search-input
            img(src="../../../../static/img/search-models.svg")
            input(
              type="text"
              placeholder="Search model"
              v-model="searchValue"
            )
          div.columns-grid.model-list-header.bold
            div.column-1 File name
            div.column-2
            div.column-3 
            div.column-4 Accuracy
            div.column-5 Loss
            div.column-6 Runtime
            div.column-7 Last Modified
          perfect-scrollbar.model-list-scrollbar
            div.models-list-row.columns-grid.model-list-item.model-list-item-dataset(
              v-for="(model, index) in computedTrainedFilteredModels" :key="model.networkID"
              :class="{'is-selected': model.isChecked}"
              )
              div.column-1
                base-checkbox.btn-checkbox(
                  :value="model.isChecked"
                  @input="(val) => handleModelSelect(val, model.networkID)"
                )
                div.editable-field.model-name-wrapper
                  bdi {{model.networkName}}
                  
              div.column-2
              div.column-3 
              div.column-4 -
              div.column-5 -
              div.column-6 {{ model && model.networkMeta && model.networkMeta.coreStatus && model.networkMeta.coreStatus.Training_Duration ? model.networkMeta.coreStatus.Training_Duration.toFixed(2) + 's' : '-' }}
              div.column-7 {{ (model && model.apiMeta && model.apiMeta.updated) ? formatDate(model.apiMeta.updated)  : ''}}
      .export-where-to.export-view
        .export-where-to-grid-parent
          .export-options
            .section-title
              .middle-text 2. Select export Option
            .divider
            div.d-flex
              .export-button(
                v-tooltip:bottom="tooltips.tensorflow"
              )
                img.c-pointer(
                  @click="openExportAsTensorflowModal"
                  role="button"
                  src="static/img/export-tensorflow.svg"
                )
              .export-button(
                v-tooltip:bottom="tooltips.fastApi"
                v-if="isServingEnabled"
              )
                img.c-pointer(
                  @click="openExportAsFastApi"
                  role="button"
                  src="static/img/export-fastapi.svg"
                )
          .export-deploy(v-if="isServingEnabled")
            .section-title
              .middle-text.bold Or Deploy Live
            .divider
            div.d-flex
              .export-button(
                v-tooltip:bottom="tooltips.gradio"
              )
                img.c-pointer(
                  v-if="isServingEnabled"
                  @click="exportGradio"
                  role="button"
                  src="static/img/export-gradio.svg"
                )
    base-global-popup(
      v-if="isTensorFlowExportOpened"
      title="Confirm Export"
      titleAlign="text-center"
      size="small"
      @closePopup="closeTensorFlowExport"
    )
      template(slot="Confirm Export-content")
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
            tr(v-if="isModalOpendFor === 'tensorflow'")
              td.bold.right Optimize:
              td.d-flex.justify-content-between
                div.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a frozen model (.pb) which\ncan be used for inference`")
                  base-checkbox(v-model="settings.Compressed") Compressed
                div.checkbox-tooltip(v-tooltip:right-wrap-text="`Produces a quantized tf-lite model which\ncan be used for edge devices`")
                  base-checkbox(v-model="settings.Quantized")  Quantized

      template(slot="action")
        button.btn.btn--default(type="button"
          @click="closeTensorFlowExport") Cancel
        button.btn.btn--primary(
          :disabled="!wasSavePathChoosen"
          type="button" 
          @click="handleExportAs"
        ) Export

</template>

<script>
import ChartSpinner from '@/components/charts/chart-spinner';
import BaseGlobalPopup from '@/components/global-popups/base-global-popup.vue';
import { mapGetters } from "vuex";
import { isModelTrained } from '@/core/modelHelpers';
import { isServingEnabled } from '@/core/helpers.js';
import cloneDeep from 'lodash.clonedeep';
import { pickDirectory as rygg_pickDirectory } from '@/core/apiRygg.js';

export default {
  name: 'ExportPage',
  components: {
    ChartSpinner,
    BaseGlobalPopup,
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
      isTensorFlowExportOpened: false,
      isModalOpendFor: null,
      searchValue: '',
      tooltips: {
        tensorflow: `<div style="white-space: normal; width: 280px;">The standard TensorFlow "saved model" format, great for if you want to use the model in an existing serving pipeline or write a small script around. Can be also be compressed and quantized from here.</div>`,
        fastApi: `<div style="white-space: normal; width: 280px;">Exports a ready-to-use serving script based on FastAPI. \n Run the script to start serving the model and then send \n requests to it to get predictions.</div>`,
        gradio: `<div style="white-space: normal; width: 280px;">Deploy the model as a Gradio app, which is a great way to demo your model for other people or just test it out on some new data.</div>`,
      }
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
    'searchValue'(strSearched) {
      console.log(strSearched);
    },
  },
  
  computed: {
    ...mapGetters({
      testStatus: 'mod_test/GET_testStatus',
      models:     'mod_workspace/GET_models',
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
    },
    computedTrainedFilteredModels() {
      const ret = this.trainedModels.filter(model => model.networkName.indexOf(this.searchValue) !== -1);
      const keepIsCheckedModelIds = ret.map(m => m.networkID);
      this.trainedModels.forEach(m => {
        if(keepIsCheckedModelIds.indexOf(m.networkID)  === -1) {
          m.isChecked = false;
        }
      })
      return ret;
    }
  },
  methods: {    
    isModelTrained(model) {
      return this.$store.dispatch('mod_api/API_checkTrainedNetwork', model.networkID);
    },
    filterTrainedModels() {
      if(!this.models.length) {
        this.trainedModels = [];
      }
      const payload = cloneDeep(this.models.filter((model) => isModelTrained(model)));
      for(let i = 0; i < payload.length; i++) {
        this.$set(payload[i], 'isChecked', false);
      }
      this.trainedModels = payload;
    },
    setExportPath(value) {
      if (value && Array.isArray(value) && value.length > 0) {
        this.settings.Location = value[0];
        this.wasSavePathChoosen = true;
      }
    },
    async saveLoadFile() {
      const selectedPath = await rygg_pickDirectory('Choose export path');
      if (selectedPath && selectedPath.path) {
        this.setExportPath([selectedPath.path])
      }
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
    checkIsAtLeastModelSelected() {
      const isModelSelected = this.trainedModels.find(m => m.isChecked);
      if(isModelSelected !== undefined) {
        return true;
      } else {
        this.$store.dispatch('globalView/GP_infoPopup', "Select model to export.", {root: true});
        return false;
      }
    },
    handleExportAs() {
      if(this.isModalOpendFor === 'tensorflow') {
        this.exportAsTensorflow();
      } else if (this.isModalOpendFor = 'fastapi') {
        this.exportAsFastApi();
      }
    },
    exportGradio() {
      if(!this.checkIsAtLeastModelSelected()) { 
        return;
      }
      this.$store.dispatch('globalView/GP_confirmPopup', {
        text: 'Gradio will open in a web browser. Click Ok to continue.',
        ok: async () => {
          const modelToExport = this.trainedModels.find(m => m.isChecked);
          const exportPayload = {
            modelId: modelToExport.networkID,
            name: modelToExport.networkName,
            Type: 'Serve Gradio',
          };
          this.loadingMessage = `Deploying model: ${modelToExport.networkName}..`;
          const retMessage = await this.$store.dispatch('mod_api/API_exportData', exportPayload);
          const gradioUrl = retMessage.substring(retMessage.indexOf('http'));
          window.open(gradioUrl, '_blank');
          this.loadingMessage = '';
        },
      });
    },
    async exportAsFastApi() {
      const modelToExport = this.trainedModels.find(m => m.isChecked);
      const exportPayload = {
        modelId: modelToExport.networkID,
        name: modelToExport.networkName,
        Type: 'FastAPI',
        Location: this.settings.Location,
      };
      this.loadingMessage = `Exporting model: ${modelToExport.networkName}.. fastaApi`;
      const retMessage = await this.$store.dispatch('mod_api/API_exportData', exportPayload);
      this.loadingMessage = '';
      this.closeTensorFlowExport();
      this.$store.dispatch('globalView/GP_infoPopup', retMessage , {root: true});
    },
    async exportAsTensorflow() { 
      const modelToExport = this.trainedModels.find(m => m.isChecked);
      const exportPayload = {
        modelId: modelToExport.networkID,
        name: modelToExport.networkName,
        Type: 'TFModel',
        Compressed: this.settings.Compressed,
        Quantized: this.settings.Quantized,
        Location: this.settings.Location,
      };
      this.loadingMessage = `Exporting model: ${modelToExport.networkName}..`;
      const retMessage = await this.$store.dispatch('mod_api/API_exportData', exportPayload);
      this.loadingMessage = '';
      this.closeTensorFlowExport();
      this.$store.dispatch('globalView/GP_infoPopup', retMessage , {root: true});
    },
    openExportAsTensorflowModal() {
      if(!this.checkIsAtLeastModelSelected()) { 
        return;
      }
      this.isModalOpendFor = 'tensorflow';
      this.isTensorFlowExportOpened = true;
    },
    openExportAsFastApi() {
      if(!this.checkIsAtLeastModelSelected()) { 
        return;
      }
      this.isModalOpendFor = 'fastapi';
      this.isTensorFlowExportOpened = true;
    },
    closeTensorFlowExport() {
      this.isTensorFlowExportOpened = false;
      this.isModalOpendFor = null;
    },
    formatDate (dateString) {
      if(!dateString) { return ''; }
      let date = new Date(dateString);
      return `${date.toLocaleDateString(navigator.language)} ${date.toLocaleTimeString([], {hour12: false})}`;
    },
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
  padding: 20px;
  padding-bottom: 0;
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

  padding: 20px;
  flex: 1;
  position: relative;

  .divider {
    border-bottom: $border-1;
    margin: 10px 0px;
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
    // width: 42px;
    // height: 42px;
    // background: #D9E2FF;

    // font-weight: bold;
    // font-size: 20px;
    // line-height: 23px;
    // display: flex;
    // justify-content: center;
    // align-items: center;

    // color: $color-6;
    // border-radius: 50%;

    // margin-right: 15px;
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

.export-page-wrapper {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(12, 1fr);
  grid-column-gap: 20px;
  padding: 20px;
  grid-row-gap: 0px;
  height: calc(100vh - 130px);
}


.export-model-list {
  height: 100%;
  grid-area: 1 / 1 / 13 / 8;
}
.export-where-to { grid-area: 1 / 8 / 13 / 13; }

.export-where-to-grid-parent {
  display: grid;
  grid-template-columns: 1fr;
grid-template-rows: repeat(12, 1fr);
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  height: 100%;
}

.export-options { grid-area: 1 / 1 / 6 / 2; }
.export-deploy { grid-area: 6 / 1 / 13 / 2; }

.width-56 {
  width: 56px;
}
.export-model-table {
  width: 100%;
  text-align: left;
}

.model-list-item {
    display: flex;
    height: 56px;
    font-size: 16px;
    font-weight: 400;
    align-items: center;
    border-radius: 4px;
    margin: 10px 0px;
    border: 1px solid transparent;

    &:hover:not(.is-selected) {
      // background: rgba(97, 133, 238, 0.75);
      // box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      background: $color-6;
      color: white;
      .is-favorite{
        path {
          fill: #E1E1E1;
        }
      }

      & .model-unsaved_changes_indicator {
        color: $color-6;
      }
      
      & .test-link {
        color: white;
        & path {
          fill: white;
        }
      }
    }
    &.is-selected {
      background: theme-var($neutral-6);
      border: 1px solid $color-6;
    }
}
.columns-grid {
  .column-1 {
    position: relative;
    margin-right: auto;
    padding-left: 80px;
    max-width: 180px;
    min-width: 180px;
    width: 180px;
    .btn-checkbox {
      position: absolute;
      left: 41px;
      top: 50%;
      transform: translateY(-50%)
    }
  }
  .column-2 {
    min-width: 210px; 
    cursor: pointer;
    display: none;
  }
  .column-3 {
    min-width: 210px;
    border: 1px solid red;
    display: none;
  }
  .column-4 {
    min-width: 170px;
    display: none;
  }
  .column-5 {
    min-width: 170px;
    display: none;
  }
  .column-6 {
    min-width: 190px;
    max-width: 190px;
  }
  .column-7 {
    min-width: 180px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;

    img {
      margin-left: 10px;
      margin-bottom: 3px
    }
  }
}
.model-list-header {
  display: flex;
  height: 43px;
  font-size: 16px;
  align-items: center;
  border-radius: 4px 4px 0px 0px;
  .column-1 {
    .btn-checkbox {
      position: absolute;
      left: 41px;
      top: 50%;
      transform: translateY(-50%)
    }
  }
  .column-6 {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
.export-button {
  background-color: $white;
  width: 160px;
  height: 64px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  margin: 0 10px;
  border: 2px solid #B6C7FB;
  transition: 0.3s !important;
  &:hover {
    border: 2px solid #6185EE;
  }
  &:active {
    background: linear-gradient(0deg, rgba(97, 133, 238, 0.2), rgba(97, 133, 238, 0.2)), #FFFFFF;
  }
}
.search-input {
    position: relative;
    width: auo;
    margin-left: 16px;
    img {
      cursor: pointer;
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      left: 10px;
    }
    input {
      padding-left: 36px;
      height: 100%;
      border: $border-1;
      border-radius: 4px;
      font-size: 14px;
      background: theme-var($neutral-7);
    }
  }
  .model-list-scrollbar {
    max-height: calc(100vh - 380px);
  }
</style>
