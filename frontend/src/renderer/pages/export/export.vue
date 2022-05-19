<template lang="pug">
chart-spinner(v-if="loadingMessage", :text="loadingMessage")
div(v-else)
  h1.export-header.bold Deploy
  .export-page-wrapper
    .export-model-list.export-view
      .section-select-model
        .section-title
          .middle-text.bold 1. Select trained models
        .divider
        .search-input
          img(src="../../../../static/img/search-models.svg")
          input(type="text", placeholder="Search model", v-model="searchValue")
        .columns-grid.model-list-header.bold
          .column-1 File name
          .column-2
          .column-3 
          .column-4 Accuracy
          .column-5 Loss
          .column-6 Runtime
          .column-7 Last Modified
        perfect-scrollbar.model-list-scrollbar
          .models-list-row.columns-grid.model-list-item.model-list-item-dataset(
            v-for="(model, index) in computedTrainedFilteredModels",
            :key="model.networkID",
            :class="{ 'is-selected': model.isChecked }"
          )
            .column-1
              base-checkbox.btn-checkbox(
                :value="model.isChecked",
                @input="(val) => handleModelSelect(val, model.networkID)"
              )
              .editable-field.model-name-wrapper
                bdi {{ model.networkName }}

            .column-2
            .column-3 
            .column-4 -
            .column-5 -
            .column-6 {{ model && model.networkMeta && model.networkMeta.coreStatus && model.networkMeta.coreStatus.Training_Duration ? model.networkMeta.coreStatus.Training_Duration.toFixed(2) + 's' : '-' }}
            .column-7 {{ model && model.apiMeta && model.apiMeta.updated ? formatDate(model.apiMeta.updated) : '' }}
    .export-where-to.export-view
      .export-where-to-grid-parent
        .export-options
          .section-title
            .middle-text.bold 2. Select Export option
          .divider
          .d-flex
            .export-button(v-tooltip:bottom="tooltips.tensorflow")
              img.c-pointer(
                @click="openExportAsTensorflowModal",
                role="button",
                src="static/img/export-tensorflow.svg"
              )
            .export-button(
              v-tooltip:bottom="tooltips.fastApi",
              v-if="isServingEnabled"
            )
              img.c-pointer(
                @click="openExportAsFastApi",
                role="button",
                src="static/img/export-fastapi.svg"
              )
            .export-button(v-tooltip:bottom="tooltips.archive")
              img.c-pointer(
                @click="openExportAsArchive",
                role="button",
                src="static/img/export-pl.svg"
              )
        .export-deploy(v-if="isServingEnabled")
          .section-title
            .middle-text.bold Or Deploy Live
          .divider
          .d-flex
            .export-button(v-tooltip:bottom="tooltips.gradio")
              img.c-pointer(
                v-if="isServingEnabled",
                @click="exportGradio",
                role="button",
                src="static/img/export-gradio.svg"
              )
  base-global-popup(
    v-if="isTensorFlowExportOpened",
    title="Confirm Export",
    titleAlign="text-center",
    size="small",
    @closePopup="closeTensorFlowExport"
  )
    template(slot="Confirm Export-content")
      .settings-table
        .row(v-if="isModalOpenedFor === 'tensorflow'")
          .bold.mb-5 Optimize:
          .d-flex.flex-column.justify-content-between
            .checkbox-tooltip(
              v-tooltip:right-wrap-text="`Produces a frozen model (.pb) which\ncan be used for inference`"
            )
              base-checkbox(v-model="settings.Compressed") Compressed
            .checkbox-tooltip(
              v-tooltip:right-wrap-text="`Produces a quantized tf-lite model which\ncan be used for edge devices`"
            )
              base-checkbox(v-model="settings.Quantized") Quantized
        
        template(v-if="isModalOpenedFor !== 'archive'")
          include ./settings-template.pug

    template(slot="action")
      button.btn.btn--default(type="button", @click="closeTensorFlowExport") Cancel
      button.btn.btn--primary(
        type="button",
        @click="handleExportAs"
      ) Export

  base-global-popup(
    v-if="isDeployModalOpened",
    :title="'Deploy to ' + isModalOpenedFor",
    titleAlign="text-center",
    size="small",
    @closePopup="closeDeployModal"
  )
    template(:slot="'Deploy to ' + isModalOpenedFor + '-content'")
      .settings-table
        .row.d-flex.align-center
          svg.popup-state-svg(
            width="22",
            height="22",
            viewBox="0 0 18 18",
            fill="none",
            xmlns="http://www.w3.org/2000/svg"
          )
            path(
              fill-rule="evenodd",
              clip-rule="evenodd",
              d="M18 9C18 11.3869 17.0518 13.6761 15.364 15.364C13.6761 17.0518 11.3869 18 9 18C6.61305 18 4.32387 17.0518 2.63604 15.364C0.948212 13.6761 0 11.3869 0 9C0 6.61305 0.948212 4.32387 2.63604 2.63604C4.32387 0.948212 6.61305 0 9 0C11.3869 0 13.6761 0.948212 15.364 2.63604C17.0518 4.32387 18 6.61305 18 9ZM9 4.5C8.85781 4.50008 8.71721 4.52994 8.58726 4.58767C8.45731 4.64539 8.3409 4.7297 8.24551 4.83515C8.15013 4.9406 8.07789 5.06487 8.03345 5.19994C7.98901 5.33501 7.97336 5.47789 7.9875 5.61937L8.38125 9.56475C8.39448 9.71974 8.4654 9.86413 8.57998 9.96934C8.69455 10.0746 8.84444 10.1329 9 10.1329C9.15556 10.1329 9.30545 10.0746 9.42002 9.96934C9.5346 9.86413 9.60552 9.71974 9.61875 9.56475L10.0125 5.61937C10.0266 5.47789 10.011 5.33501 9.96655 5.19994C9.92211 5.06487 9.84987 4.9406 9.75449 4.83515C9.6591 4.7297 9.54269 4.64539 9.41274 4.58767C9.28279 4.52994 9.14219 4.50008 9 4.5ZM9.00225 11.25C8.70388 11.25 8.41773 11.3685 8.20675 11.5795C7.99578 11.7905 7.87725 12.0766 7.87725 12.375C7.87725 12.6734 7.99578 12.9595 8.20675 13.1705C8.41773 13.3815 8.70388 13.5 9.00225 13.5C9.30062 13.5 9.58677 13.3815 9.79774 13.1705C10.0087 12.9595 10.1272 12.6734 10.1272 12.375C10.1272 12.0766 10.0087 11.7905 9.79774 11.5795C9.58677 11.3685 9.30062 11.25 9.00225 11.25Z",
              fill="#B6C7FB"
            )
          | &nbsp;Gradio will open in a web browser.

        include ./settings-template.pug

    template(slot="action")
      button.btn.btn--default(type="button", @click="closeDeployModal") Cancel
      button.btn.btn--primary(type="button", @click="handleDeployFor") Deploy
</template>

<script>
import ChartSpinner from "@/components/charts/chart-spinner";
import BaseGlobalPopup from "@/components/global-popups/base-global-popup.vue";
import { mapGetters } from "vuex";
import { isModelTrained } from "@/core/modelHelpers";
import { isServingEnabled } from "@/core/helpers.js";
import cloneDeep from "lodash.clonedeep";
import { pickDirectory as rygg_pickDirectory } from "@/core/apiRygg.js";
import { renderingKernel } from "@/core/apiRenderingKernel.js";

export default {
  name: "ExportPage",
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
        { text: "TensorFlow Model", value: "TFModel" },
        { text: "Jupyter Notebook", value: "ipynb" },
        { text: "FastAPI Server", value: "FastAPI" },
        { text: "Serve Gradio", value: "Serve Gradio" },
      ],
      settings: {
        Location: "",
        Type: "TFModel",
        Compressed: false,
        Quantized: false,
        name: "",
        ExcludePreProcessing: false,
        ExcludePostProcessing: false,
      },
      loadingMessage: "",
      wasSavePathChosen: false,
      isTensorFlowExportOpened: false,
      isModalOpenedFor: null,
      isDeployModalOpened: false,
      searchValue: "",
      tooltips: {
        tensorflow: `<div style="white-space: normal; width: 280px;">The standard TensorFlow "saved model" format, great for if you want to use the model in an existing serving pipeline or write a small script around. Can be also be compressed and quantized from here.</div>`,
        fastApi: `<div style="white-space: normal; width: 280px;">Exports a ready-to-use serving script based on FastAPI. \n Run the script to start serving the model and then send \n requests to it to get predictions.</div>`,
        gradio: `<div style="white-space: normal; width: 280px;">Deploy the model as a Gradio app, which is a great way to demo your model for other people or just test it out on some new data.</div>`,
        archive: `<div style="white-space: normal; width: 280px;">Export as a PerceptiLabs archive, which is useful for sharing your work with other users.</div>`,
      },
    };
  },
  watch: {
    models(m) {
      this.filterTrainedModels();
    },
    "settings.Quantized"(value) {
      if (value) {
        this.settings.Compressed = false;
      }
    },
    "settings.Compressed"(value) {
      if (value) {
        this.settings.Quantized = false;
      }
    },
  },

  computed: {
    ...mapGetters({
      testStatus: "mod_test/GET_testStatus",
      models: "mod_workspace/GET_models",
    }),
    checkedModelsLength() {
      return (
        this.trainedModels && this.trainedModels.filter(m => m.isChecked).length
      );
    },
    isAllModelsChecked() {
      const trainedModelsLength = this.trainedModels.length;
      return trainedModelsLength === this.checkedModelsLength;
    },
    isServingEnabled() {
      return isServingEnabled();
    },
    computedTrainedFilteredModels() {
      const ret = this.trainedModels.filter(
        model => model.networkName.indexOf(this.searchValue) !== -1,
      );
      const keepIsCheckedModelIds = ret.map(m => m.networkID);
      this.trainedModels.forEach(m => {
        if (keepIsCheckedModelIds.indexOf(m.networkID) === -1) {
          m.isChecked = false;
        }
      });
      return ret;
    },
  },
  methods: {
    isModelTrained(model) {
      return this.$store.dispatch(
        "mod_api/API_checkTrainedNetwork",
        model.networkID,
      );
    },
    async filterTrainedModels() {
      if (!this.models.length) {
        this.trainedModels = [];
      }
      let promiseArray = [];
      for (let i = 0; i < this.models.length; i++) {
        promiseArray.push(this.$store.dispatch(
          "mod_api/API_getModelStatus",
          this.models[i].networkID,
        ));
      }
      await Promise.all(promiseArray);
      const payload = cloneDeep(
        this.models.filter(model => isModelTrained(model)),
      );
      for (let i = 0; i < payload.length; i++) {
        this.$set(payload[i], "isChecked", false);
      }
      this.trainedModels = payload;
    },
    setExportPath(value) {
      if (value && Array.isArray(value) && value.length > 0) {
        this.settings.Location = value[0];
        this.wasSavePathChosen = true;
      }
    },
    async saveLoadFile() {
      const selectedPath = await rygg_pickDirectory("Choose export path");
      if (selectedPath && selectedPath.path) {
        this.setExportPath([selectedPath.path]);
      }
    },
    handleModelSelect(isChecked, modelId) {
      let modelIndex = null;
      for (let i = 0; i < this.trainedModels.length; i++) {
        this.$set(this.trainedModels[i], "isChecked", false);
        if (modelId === this.trainedModels[i].networkID) {
          modelIndex = i;
        }
      }
      if (isChecked) {
        this.$set(this.trainedModels[modelIndex], "isChecked", true);
      }
    },
    checkIsAtLeastModelSelected() {
      const isModelSelected = this.trainedModels.find(m => m.isChecked);
      if (isModelSelected !== undefined) {
        return true;
      } else {
        this.$store.dispatch(
          "globalView/GP_infoPopup",
          "Select model to export.",
          { root: true },
        );
        return false;
      }
    },
    handleExportAs() {
      if (this.isModalOpenedFor === "tensorflow") {
        this.exportAs("TFModel");
      } else if (this.isModalOpenedFor === "fastapi") {
        this.exportAs("FastAPI");
      } else if (this.isModalOpenedFor === "archive") {
        this.exportAs("PlPackage");	
      }
    },
    handleDeployFor() {
      if (this.isModalOpenedFor === 'Gradio') {
        this.deployAsGradio();
      }
    },
    async deployAsGradio() {
      const modelToExport = this.trainedModels.find(m => m.isChecked);
      const exportPayload = {
        modelId: modelToExport.networkID,
        name: modelToExport.networkName,
        Type: "Serve Gradio",
        ExcludePreProcessing: this.settings.ExcludePreProcessing,
        ExcludePostProcessing: this.settings.ExcludePostProcessing
      };
      this.loadingMessage = `Deploying model: ${modelToExport.networkName}..`;
      const retMessage = await this.$store.dispatch(
        "mod_api/API_exportData",
        exportPayload,
      );
      const gradioUrl = retMessage.substring(retMessage.indexOf("http"));
      const popup = window.open(gradioUrl, "_blank");
      if (!popup) {
        this.$store.dispatch(
          "globalView/GP_infoPopup",
          `Open <a href="${gradioUrl}" target="_blank" style="color: #6185EE;">${gradioUrl}</a> to run Gradio`,
          { root: true },
        );
      }
      this.loadingMessage = "";
    },
    exportGradio() {
      if (!this.checkIsAtLeastModelSelected()) {
        return;
      }
      
      this.isDeployModalOpened = true;
      this.isModalOpenedFor = 'Gradio';
    },
    closeDeployModal() {
      this.isDeployModalOpened = false;
      this.isModalOpenedFor = null;
    },
    async exportAs(type) {
      const modelToExport = this.trainedModels.find(m => m.isChecked);
      const exportPayload = {
        modelId: modelToExport.networkID,
        name: modelToExport.networkName,
        Type: type,
        Compressed: this.settings.Compressed,
        Quantized: this.settings.Quantized,
        Location: this.settings.Location,
        ExcludePreProcessing: this.settings.ExcludePreProcessing,
        ExcludePostProcessing: this.settings.ExcludePostProcessing
      };
      this.loadingMessage = `Exporting model: ${modelToExport.networkName}..`;
      const url = await this.$store.dispatch(
        "mod_api/API_exportData",
        exportPayload,
      );
      this.loadingMessage = "";
      this.closeTensorFlowExport();

      renderingKernel.downloadFile(url);
    },
    openExportAsTensorflowModal() {
      if (!this.checkIsAtLeastModelSelected()) {
        return;
      }
      this.isModalOpenedFor = "tensorflow";
      this.isTensorFlowExportOpened = true;
    },
    openExportAsFastApi() {
      if (!this.checkIsAtLeastModelSelected()) {
        return;
      }
      this.isModalOpenedFor = "fastapi";
      this.isTensorFlowExportOpened = true;
    },
    openExportAsArchive() {
      if (!this.checkIsAtLeastModelSelected()) {
        return;
      }
      this.isModalOpenedFor = "archive";
      this.isTensorFlowExportOpened = true;
    },
    closeTensorFlowExport() {
      this.isTensorFlowExportOpened = false;
      this.isModalOpenedFor = null;

      this.$store.dispatch(
        "globalView/GP_infoPopup",
        "Model has successfully exported to your Downloads folder",
      );
    },
    formatDate(dateString) {
      if (!dateString) {
        return "";
      }
      let date = new Date(dateString);
      return `${date.toLocaleDateString(
        navigator.language,
      )} ${date.toLocaleTimeString([], { hour12: false })}`;
    },
  },
};
</script>

<style lang="scss" scoped>
@keyframes clickMeFrame {
  0% {
    box-shadow: 0 0 3px #6185ee;
  }
  50% {
    box-shadow: 0 0 10px #6185ee;
  }
  100% {
    box-shadow: 0 0 3px #6185ee;
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
  margin-bottom: 10px;

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

.settings-table {
  padding: 0 40px;
  font-size: 14px;

  .row {
    margin-bottom: 20px;
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
.export-where-to {
  grid-area: 1 / 8 / 13 / 13;
}

.export-where-to-grid-parent {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: repeat(12, 1fr);
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  height: 100%;
}

.export-options {
  grid-area: 1 / 1 / 6 / 2;
}
.export-deploy {
  grid-area: 6 / 1 / 13 / 2;
}

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
    .is-favorite {
      path {
        fill: #e1e1e1;
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
      transform: translateY(-50%);
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
      margin-bottom: 3px;
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
      transform: translateY(-50%);
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
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  margin: 0 10px;
  border: 2px solid $white;
  transition: 0.3s !important;
  &:hover {
    border: 2px solid #6185ee;
  }
  &:active {
    background: linear-gradient(
        0deg,
        rgba(97, 133, 238, 0.2),
        rgba(97, 133, 238, 0.2)
      ),
      #ffffff;
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
