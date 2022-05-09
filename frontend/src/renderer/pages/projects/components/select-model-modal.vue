<template lang="pug">
div
  base-global-popup.select-model(
    :title="getModalTitle",
    :closeOnOutside="!isCreateModelLoading",
    titleAlign="text-center",
    @closePopup="() => closeModal()"
  )
    template(:slot="getModalTitle + '-content'")
      template(v-if="onStep === STEP.TYPE")
        .select-type-wrapper.c-pointer
          .select-type-contents
            .select-type-item(
              v-for="type in trainingModes",
              :key="type.id",
              @click="handleChoosingModelType(type.modelType)"
              :class="{'selected': type.modelType === modelType}"
            )
              img(:src="type.imgPath")
              .title.bold {{ type.title }}
              p.desc {{ type.description }}
          //- div.text-center.find-out-message If you do not have your own dataset,
          //-   span.guide-link(@click="openPLVideoTutorialPage") click here
          //-   | to use a prepared dataset

      .w-100(v-else)
        div(v-show="onStep === STEP.LOAD_CSV")
          load-dataset(
            v-if="isPublicDatasetEnabled",

            @handleDataPathUpdates="handleDataPathUpdates",

            @handleImageClassificationNext="handleImageClassificationNext",
            @handleImageSegmentationNext="handleImageSegmentationNext",
            @handleMultiModalNext="handleMultiModalNext",
            @handleObjectDetectionNext="handleObjectDetectionNext",

            :modelType="modelType",
            @back="gotoTypeStep",
            :uploadStatus="uploadStatus"
          )
          template(v-else)
            .main-file-structure-contents
              .load-contents-group
                button.btn.btn--primary.load-dataset(
                  @click="openFilePicker('setDataPath')"
                ) Upload .CSV
            .find-out-message Find our starting guide
              span.guide-link(@click="openPLVideoTutorialPage") here.

        .dataset-settings(v-show="onStep === STEP.PARTITION")
          chart-spinner(v-if="showLoadingSpinner")
          template(v-if="isCreateModelLoading")
            chart-spinner(:text="buildingPreProcessingStatus")
            error-cta.cta-container(v-if="isShowCTA")
          template(v-else-if="dataset")
            .form_row
              .form_label Name:
              .form_input
                input.normalize-inputs(
                  type="text",
                  v-model="modelName",
                  @keyup="onModelNameKeyup"
                )
            .form_row.relative.mb-15(v-if="isEnterpriseMode !== true")
              .form_label Model Path:
              .form_input.input_group.form_row
                input.normalize-inputs(type="text", v-model="modelPath")
                button.btn.btn--primary.normalize-button(
                  type="button",
                  @click="openFilePicker"
                ) Browse
            perfect-scrollbar.fix-for-scroll-bar-place(
              style="padding-bottom: 180px"
            )
              csv-table(
                v-if="dataset",
                :dataSet="dataset",
                :dataSetTypes="dataSetTypes",
                @update="handleCSVDataTypeUpdates",
                :modelType="modelType"
              )

            data-column-option-sidebar(
              :key="index",
              v-for="index in csvData && csvData.dataTypes.length",
              :columnSelectedType="csvData && csvData.dataTypes",
              :columnNames="csvData && csvData.columnNames",
              @handleChange="updatePreprocessingTypes",
              :elementIndex="index - 1",
              :modelType="modelType"
            )
            div(style="margin-top: -180px")
              span.default-text.error(
                v-if="modelType !== modelTypes.OBJECT_DETECTION && isAllIOTypesFilled() && !hasInputAndTarget()"
              ) Make sure to have at least one input and one target to proceed
              span.default-text.error(
                v-else-if="modelType !== modelTypes.OBJECT_DETECTION && isAllIOTypesFilled() && !hasOneTarget()"
              ) Make sure to have only one target to proceed

              .data-partition-wrapper
                h5.default-text Data partition:
                triple-input(
                  style-type="darken",
                  v-model="datasetSettings.partitions",
                  separate-sign="%",
                  :validate-min="1",
                  :validate-max="98",
                  :validate-sum="100",
                  :withLabels="true"
                )
              div(style="display: flex; align-itmes: center")
                info-tooltip(
                  text="Select random samples to place in each partition, good practice if your dataset is ordered"
                )
                base-checkbox(
                  style="font-size: 14px; white-space: nowrap",
                  v-model="datasetSettings.randomizedPartitions"
                ) Randomize partition

              .random-seed-input-wrapper.form_row.relative
                h5.default-text Seed:
                input.random-seed-input(
                  type="text",
                  v-model="datasetSettings.randomSeed"
                )
      //- div.d-flex.justify-content-center(v-show="onStep === STEP.TRAINING")
        //-   template(v-if="isCreateModelLoading")
        //-     chart-spinner(text="Building preprocessing pipelines...")
        //-     error-cta.cta-container(v-if="isShowCTA") 

    template(
      slot="action",
      v-if="onStep === STEP.PARTITION && !showLoadingSpinner && !isCreateModelLoading"
    )
      button.link.reload-dataset-btn(@click="toPrevStep")
        img(src="/static/img/back-arrow.svg")
        | Reload dataset
      .d-flex.align-items-center
        .image-format-message *.jpg .png .jpeg .tiff only
        .d-flex
          button.btn.btn--primary(
            :class="{ disabled: isDisableCreateAction() }",
            :disabled="isDisableCreateAction()",
            @click="createModelTF2X(false)"
          ) Create
    template(slot="action", v-if="onStep === STEP.PUBLIC_LIST")
    template(v-else)
      | Error
</template>
<script>
import CsvTable from "@/components/different/csv-table.vue";
import TripleInput from "@/components/base/triple-input";
import InfoTooltip from "@/components/different/info-tooltip.vue";
import ChartSpinner from "@/components/charts/chart-spinner";
import {
  defaultTrainingSettings,
  PERCEPTILABS_VIDEO_TUTORIAL_URL,
} from "@/core/constants";
import { mapActions, mapState, mapGetters } from "vuex";
import mixinFocus from "@/core/mixins/net-element-settings-input-focus.js";
import DataColumnOptionSidebar from "@/components/different/data-column-option-sidebar";
import ErrorCta from "@/components/error-cta";
import {
  convertModelRecommendationToVisNodeEdgeList,
  createVisNetwork,
} from "@/core/helpers/layer-positioning-helper";

import { buildLayers } from "@/core/helpers/layer-creation-helper";
import BaseGlobalPopup from "@/components/global-popups/base-global-popup";
import { assembleModel } from "@/core/helpers/model-helper";

import {
  debounce,
  isPublicDatasetEnabled,
} from "@/core/helpers";
import {
  doesDirExist as rygg_doesDirExist,
  getModel as rygg_getModel,  
  getDatasetContent as rygg_getDatasetContent,
  getNextModelName as rygg_getNextModelName,
  createDataset as rygg_createDataset,
  getDataset as rygg_getDataset,
  uploadDatasetToFileserver as rygg_uploadDatasetToFileserver,
  pickFile as rygg_pickFile,
  pickDirectory as rygg_pickDirectory,
  createClassificationDataset as rygg_createClassificationDataset,
  createEnterpriseClassificationDataset as rygg_createEnterpriseClassificationDataset,
  createSegmentationDataset as rygg_createSegmentationDataset,
  createEnterpriseSegmentationDataset as rygg_createEnterpriseSegmentationDataset,
  isTaskComplete as rygg_isTaskComplete,
} from "@/core/apiRygg";
import { renderingKernel } from "@/core/apiRenderingKernel";
import { makeDatasetSettings } from "@/core/helpers";

import LoadDataset from "./load-dataset.vue";
import { modelTypes, objectDetectionDataTypes } from "@/core/constants";
import { whenCeleryTaskDone } from "@/core/helpers";
const STEP = {
  LOAD_CSV: 1,
  PARTITION: 2,
  TRAINING: 3,
  PUBLIC_LIST: 4,
  TYPE: 5,
  CLASS: 6,
};

export default {
  name: "SelectModelModal",
  components: {
    BaseGlobalPopup,
    CsvTable,
    TripleInput,
    InfoTooltip,
    ChartSpinner,
    DataColumnOptionSidebar,
    ErrorCta,
    LoadDataset,
  },
  mixins: [mixinFocus],
  created() {
    // Check if Rygg is online
    this.checkRyggAvailability().then(isRyggAvailable => {
      if (!isRyggAvailable) {
        this.closeModal();
      }
    });
    const showNewModelPopup = this.showNewModelPopup;

    if (
      typeof showNewModelPopup === "object" &&
      showNewModelPopup !== null &&
      showNewModelPopup.hasOwnProperty("datasetId")
    ) {
      const allDatasets = this.$store.getters["mod_datasets/GET_datasets"];
      const ds = allDatasets.find(ds => ds.dataset_id === showNewModelPopup.datasetId);
      this.setModelType(ds.type);
      this.handleDataPathUpdates([ds.location]);
    }
  },
  data: function() {
    return {
      STEP: STEP,
      modelTypes: modelTypes,
      trainingModes: [
        {
          id: 1,
          title: "Image Classification",
          description: "Train your model to classify images",
          imgPath: "./static/img/project-page/upload-class.jpg",
          modelType: modelTypes.CLASSIFICATION
        },
        {
          id: 2,
          title: "Segment Images",
          description: "Train your model to segment things in images",
          imgPath: "./static/img/project-page/upload-segment.jpg",
          modelType: modelTypes.SEGMENTATION
        },
        {
          id: 3,
          title: "Multi-Modal",
          description:
            "Combined data types, inputs and targets for more complex problems",
          imgPath: "./static/img/project-page/upload-multi.jpg",
          modelType: modelTypes.MULTI_MODAL
        },
        process.env.ENABLE_OBJECT_DETECTION === 'true' && {
          id: 4,
          title: "Object Detection",
          description: "Train your model to find objects in images",
          imgPath: "./static/img/project-page/upload-object-detection.jpg",
          modelType: modelTypes.OBJECT_DETECTION
        },
      ].filter(v => !!v),
      chosenTemplate: null,
      
      modelName: "",
      description: "",
      modelPath: "",
      hasChangedModelName: false,
      csvData: null, // parsed dataset and meta
      dataset: null,
      datasetPath: null,
      dataSetTypes: [],
      datasetSettings: {
        randomizedPartitions: true,
        partitions: [70, 20, 10],
        randomSeed: "123",
      },
      debouncedCreateModelFunction: null,
      onStep: 5,
      settings: defaultTrainingSettings,
      showLoadingSpinner: false,
      isCreateModelLoading: false,
      createdFromDatasetId: null,
      isShowCTA: false,
      buildingPreProcessingStatus: "Building preprocessing pipelines...",
      modelType: "",
      isFilePickerOpened: false,
      uploadStatus: "",
    };
  },
  computed: {
    ...mapState({
      currentProjectId: state => state.mod_project.currentProject,
      workspaces: state => state.mod_workspace.workspaceContent,
      startupDatasetPath: state => state.mod_datasetSettings.startupFolder,
      showNewModelPopup: state =>
        state.globalView.globalPopup.showNewModelPopup,
    }),
    ...mapGetters({
      currentProject: "mod_project/GET_project",
      projectPath: "mod_project/GET_projectPath",
      currentNetworkId: "mod_workspace/GET_currentNetworkId",
      userEmail: "mod_user/GET_userEmail",
      isEnterpriseMode: "globalView/get_isEnterpriseApp",
    }),
    isPublicDatasetEnabled() {
      return isPublicDatasetEnabled();
    },
    isDataWizardEnabled() {
      return isEnvDataWizardEnabled();
    },
    isFolderLoadingEnabled() {
      return isFolderLoadingEnabled();
    },
    getModalTitle() {
      switch (this.onStep) {
        case STEP.LOAD_CSV:
          switch (this.modelType) {
            case this.modelTypes.CLASSIFICATION:
              return "Image Classification";
            case this.modelTypes.SEGMENTATION:
              return "Image Segmentation";
            case this.modelTypes.MULTI_MODAL:
              return "Multi-Modal";
            case this.modelTypes.OBJECT_DETECTION:
              return "Object Detection";
          }
        case STEP.PARTITION:
          return "Define your dataset";
        case STEP.TRAINING:
          return "Training settings";
        case STEP.PUBLIC_LIST:
          return "Load dataset";
        case STEP.TYPE:
          return "What do you want to do?";
      }
    },
    
  },
  mounted() {
    document.addEventListener("keydown", this.keysNavigationHandler);
    this.modelPath = this.projectPath;

    this.debouncedCreateModelFunction = debounce(_ => {
      this.createModel();
    }, 1000);
  },
  beforeDestroy() {},
  destroyed() {
    document.removeEventListener("keydown", this.keysNavigationHandler);
  },
  methods: {
    ...mapActions({
      addNetwork: "mod_workspace/ADD_network",
      closeStatsTestViews: "mod_workspace/SET_statisticsAndTestToClosed",
      currentProjectModels: "mod_project/getProjectModels",
      getModelMeta: "mod_project/getModel",
      getProjects: "mod_project/getProjects",
      showErrorPopup: "globalView/GP_errorPopup",
      checkRyggAvailability: "mod_api/checkRyggAvailability",
    }),
    keysNavigationHandler(event) {
      event.stopPropagation();

      const key = event.key;
      if (key === "Escape") {
        this.closeModal();
      }
    },
    closeModal() {
      this.$store.dispatch("globalView/SET_newModelPopup", false);
    },
    choseTemplate(index) {
      this.chosenTemplate = index;
      this.autoPopulateName();
    },
    async autoPopulateName() {
      if (this.modelName && this.hasChangedModelName) {
        return;
      }
      let namePrefix = "Model";

      this.modelName = await rygg_getNextModelName(namePrefix);
    },
    isAllIOTypesFilled() {
      const { csvData } = this;
      return (
        csvData &&
        csvData.ioTypes.filter(v => v !== undefined).length ===
          csvData.ioTypes.length
      );
    },
    isAllDataTypesFilled() {
      const { csvData } = this;
      return (
        csvData &&
        csvData.dataTypes.filter(v => v !== undefined).length ===
          csvData.dataTypes.length
      );
    },
    hasInputAndTarget() {
      const { csvData } = this;
      return (
        csvData &&
        csvData.ioTypes.filter(v => v === "Input").length > 0 &&
        csvData.ioTypes.filter(v => v === "Target").length > 0
      );
    },
    hasOneTarget() {
      const { csvData } = this;
      return (
        csvData && csvData.ioTypes.filter(v => v === "Target").length === 1
      );
    },
    isDisableCreateAction() {
      const allColumnsAreSelected = this.isAllIOTypesFilled();
      const hasInputAndTarget = this.hasInputAndTarget();
      const hasOneTarget = this.hasOneTarget();
      const isObjectDetection = this.modelType === modelTypes.OBJECT_DETECTION;
      
      return (!isObjectDetection && (!allColumnsAreSelected || !hasInputAndTarget || !hasOneTarget)) || (isObjectDetection && (!allColumnsAreSelected || !this.isAllDataTypesFilled()));
    },
    async createModel() {
      await this.createModelTF2X();
    },
    async createModelTF2X(runStatistics = false) {
      if (!this.csvData) {
        throw new Error("csv is required");
      }

      const { modelName, modelPath } = this;
      if (!(await this.isValidModelName(modelName))) {
        return this.showErrorPopup(
          `The model name "${modelName}" already exists.`,
        );
      }

      if (!(await this.isValidDirName(modelName, modelPath))) {
        return this.showErrorPopup(
          `The "${modelName}" folder already exists at "${modelPath}".`,
        );
      }

      this.isCreateModelLoading = true;

      this.isShowCTA = false;
      const watchTimerId = setTimeout(() => {
        this.isShowCTA = true;
      }, 3 * 60 * 1000);

      // Creating the project/network entry in rygg

      const datasetSettings = makeDatasetSettings(
        this.datasetSettings.randomizedPartitions,
        this.datasetSettings.partitions,
        this.datasetSettings.randomSeed,
        this.csvData,
        this.createdFromDatasetId,
      );

      const userEmail = this.userEmail;

      await renderingKernel.waitForDataReady(
        datasetSettings,
        userEmail,
        message => {
          this.buildingPreProcessingStatus = message;
        },
        err => {
          this.showErrorPopup(err.details);
          this.closeModal();
        }
      );

      const [modelId, modelRecommendation] = await renderingKernel
        .getModelRecommendation(
          this.currentProjectId,
          this.createdFromDatasetId,
          datasetSettings,
          this.userEmail,
          modelName,
          runStatistics,
          this.isEnterpriseMode ? null : this.modelPath 
        )
        .then(res => {
          if (res && res.error) {
            this.showErrorPopup(
              res.error.message + "\n\n" + res.error.details
            );
            this.isCreateModelLoading = false;      
          }
          return [res['model_id'], res['graph_settings']];
        })
        .catch(err => {
          this.showErrorPopup(
            res.error.message + "\n\n" + res.error.details
          );
          this.isCreateModelLoading = false;      
          return null;
        });

      if (!modelRecommendation) {
        this.closeModal();
      }

      const inputData = convertModelRecommendationToVisNodeEdgeList(
        modelRecommendation,
      );
      const network = createVisNetwork(inputData);

      // Wait till the 'stabilized' event has fired
      await new Promise(resolve =>
        network.on("stabilized", async data => resolve()),
      );

      // Creating the networkElementList for the network
      var ids = inputData.nodes.getIds();
      var nodePositions = network.getPositions(ids);
      const layerMeta = await buildLayers(modelRecommendation, nodePositions);

      // Kernel has created a model. Get the meta info from Rygg
      console.log(`Get apiMeta from Rygg for model ${modelId}`)
      const apiMeta = await rygg_getModel(modelId);

      let frontendSettings = {
        apiMeta: apiMeta,
        networkName: modelName,
        networkMeta: null, // Use default
        layerMeta: layerMeta,
      };

      const newNetwork = assembleModel(
        datasetSettings,
        this.settings,
        modelRecommendation,
        frontendSettings,
      );

      await this.$store.dispatch("mod_workspace/setViewType", "model");
      await this.addNetwork({ newNetwork: newNetwork }).then(() => {
        if (runStatistics) {
          setTimeout(() => {
            this.$store.dispatch("mod_events/EVENT_set_eventRunStatistic");
          }, 0);
        }
      });

      // Swapping view so that the newly created model is shown
      // TODO: break apart this views
      await this.$store.dispatch(
        "mod_workspace/SET_statisticsAndTestToClosed",
        { networkId: this.currentNetworkId },
      );
      await this.$store.dispatch(
        "mod_workspace/SET_currentModelIndexByNetworkId",
        apiMeta.model_id,
      );
      await this.$store.dispatch("mod_workspace/setViewType", "model");

      this.$store.commit("mod_empty-navigation/set_emptyScreenMode", 0);

      this.isCreateModelLoading = false;
      clearTimeout(watchTimerId);
      this.closeModal();
    },
    async openFilePicker(openFilePickerReason) {
      if (openFilePickerReason === "setDataPath") {
        if (this.isEnterpriseMode) {
          this.loadDataset();
        } else {
          this.isFilePickerOpened = true;
          const selectedDataset = await rygg_pickFile(
            "Choose data to load",
            this.startupDatasetPath,
            [{ extensions: ["*.csv"] }],
          );
          this.isFilePickerOpened = false;

          if (selectedDataset && selectedDataset.path) {
            await this.handleDataPathUpdates([selectedDataset.path]);
          }
        }
      } else {
        const selectedDirectory = await rygg_pickDirectory(
          "Choose Model path",
          this.modelPath,
        );

        if (selectedDirectory && selectedDirectory.path) {
          this.updateModelPath([selectedDirectory.path]);
        }
      }
    },
    validDirPath(url) {
      if ((url.length > 3 && url.slice(-1) === "/") || url.slice(-1) === "\\") {
        return url.slice(0, -1);
      }
      return url;
    },
    updateModelPath(filepath) {
      this.modelPath =
        filepath && filepath[0] ? this.validDirPath(filepath[0]) : "";
    },

    onModelNameKeyup() {
      if (this.modelName === "") {
        this.hasChangedModelName = false;
      } else {
        this.hasChangedModelName = true;
      }
    },
    async handleDataPathUpdates(dataPath, datasetName="") {
      if (!dataPath || !dataPath.length || !dataPath[0]) {
        return;
      }
      try {
        this.showLoadingSpinner = true;
        this.toNextStep();
        if (!this.isEnterpriseMode) {
          this.$store.dispatch(
            "mod_datasetSettings/setStartupFolder",
            dataPath[0].match(/(.*)[\/\\]/)[1] || "",
          );
        }

        // create Dataset or User existing one
        await this.$store.dispatch("mod_datasets/getDatasets");
        const allDatasets = this.$store.getters["mod_datasets/GET_datasets"];
        const datasetIndex = allDatasets
          .map(x => x.location)
          .indexOf(dataPath[0]);
        if (datasetIndex !== -1) {
          this.createdFromDatasetId = allDatasets[datasetIndex].dataset_id;
        } else {
          const createDataset = await rygg_createDataset({
            name: datasetName,
            location: dataPath[0],
            type: this.modelType,
          });
          this.$store.dispatch("mod_datasets/getDatasets");
          this.createdFromDatasetId = createDataset.data.dataset_id;
        }

        const datasetContentPath = dataPath[0];
        const fileContents = await rygg_getDatasetContent(
          this.createdFromDatasetId,
        );

        if (this.modelType === modelTypes.OBJECT_DETECTION) {
          // HARDCODED
          // Kernel does not support /datasets/type_inference for dataset yet, so hard code on the frontend
          this.dataSetTypes = fileContents[0].split(',').reduce((acc, columnName, index) => ({
            ...acc,
            [columnName]: [objectDetectionDataTypes, index]
          }), {});
        } else {
          this.dataSetTypes = await renderingKernel
            .getDataTypes(this.createdFromDatasetId, this.userEmail)
            .then(res => {
              if (res.error) {
                this.showErrorPopup(
                  res.error.message + "\n\n" + res.error.details,
                );
                this.showLoadingSpinner = false;
              }
              return res;
            })
            .catch(err => {
              console.error(err);
              this.showErrorPopup(
                "Error: Couldn't infer data types due to an exception: " + err,
              );
              this.showLoadingSpinner = false;
              return null;
            });
        }

        if (this.dataSetTypes && fileContents) {
          this.dataset = fileContents;
          this.datasetPath = datasetContentPath;
          this.autoPopulateName();
        } else {
          this.closeModal();
        }
      } catch (err) {
        if (err.message) {
          this.showErrorPopup(err.message);
        }
        this.toPrevStep();
      } finally {
        this.showLoadingSpinner = false;
      }
    },
    handleCSVDataTypeUpdates(payload) {
      this.csvData = payload;
    },
    async isValidModelName(modelName) {
      if (!modelName) {
        return;
      }

      const modelMeta = await this.currentProjectModels();
      const modelNames = modelMeta.map(x => x.name);

      // Making sure name is not already in the list
      return modelNames.indexOf(modelName) === -1;
    },
    async isValidDirName(modelName, modelPath) {
      const dirAlreadyExist = await rygg_doesDirExist(
        `${modelPath}/${modelName}`,
      );

      return !dirAlreadyExist;
    },
    toNextStep() {
      if (this.onStep === STEP.TYPE) {
        if (this.showNewModelPopup && this.showNewModelPopup.datasetId) {
          this.onStep = STEP.PARTITION;
        } else {
          this.onStep = STEP.LOAD_CSV;
        }
      } else if (this.onStep === STEP.PUBLIC_LIST) {
        this.onStep = STEP.PARTITION;
      } else {
        this.onStep += 1;
      }
    },
    toPrevStep() {
      this.onStep -= 1;
    },
    gotoTypeStep() {
      this.onStep = STEP.TYPE;
    },
    goToPublicDatasets() {
      this.onStep = STEP.PUBLIC_LIST;
    },
    openPLVideoTutorialPage() {
      window.open(PERCEPTILABS_VIDEO_TUTORIAL_URL, "_blank");
    },
    updatePreprocessingTypes(numColumn, value) {
      this.csvData.preprocessingTypes.splice(numColumn, 1, value);
    },
    onAddClass() {
      this.classList.push({
        id: this.classList.length + 1,
        name: "Class " + (this.classList.length + 1),
        images: [],
      });
    },
    onAddClassImages() {},
    loadDataset() {
      const fileInput = document.createElement("input");
      fileInput.setAttribute("type", "file");
      fileInput.setAttribute("accept", ".csv,.zip");
      fileInput.addEventListener("change", e => {
        const file = e.target.files[0];
        rygg_uploadDatasetToFileserver(file, false, this.modelType)
          .then(async () => {
            this.handleDataPathUpdates([file.name]);
          })
          .catch(async e => {
            if (
              e.response.data ===
              `File ${file.name} exists and overwrite is false`
            ) {
              this.handleDataPathUpdates([file.name]);
            }
          });
      });
      fileInput.click();
    },
    handleChoosingModelType(modelType) {
      this.setModelType(modelType);
      this.toNextStep();
    },
    setModelType(modelType) {
      if (!Object.values(this.modelTypes).includes(modelType)) {
        throw new Error(`${modelType} is not allowed props`);
      }
      this.modelType = modelType;
    },
    async handleImageClassificationNext(datasetName, imageClassificationFolderPath) {
      if (this.isEnterpriseMode) {
        return this.handleEnterpriseImageClassificationNext(datasetName, imageClassificationFolderPath);
      }
      const {
        dataset_location,
        task_id,
      } = await rygg_createClassificationDataset(
        imageClassificationFolderPath,
        datasetName
      );
      await whenCeleryTaskDone(task_id);
      await this.handleDataPathUpdates([dataset_location], datasetName);
    },
    async handleEnterpriseImageClassificationNext(datasetName, imageClassificationFolderPath) {
      this.uploadStatus = "Processing...";

      try {
        const { task_id, dataset_id } = await rygg_createEnterpriseClassificationDataset(
          imageClassificationFolderPath,
          datasetName
        );

        await whenCeleryTaskDone(task_id, cb => this.handleUploadProgress(cb));

        const response = await rygg_getDataset(dataset_id);
        const { data: { location: path } = {} } = response;

        if (path) await this.handleDataPathUpdates([path], datasetName);
      } catch (err) {
        if (err.message) {
          this.$store.dispatch("globalView/GP_errorPopup", err.message);
        }
      } finally {
        this.uploadStatus = "";
      }
    },
    async handleImageSegmentationNext(datasetName, imageSegmentationImageFolderPath, imageSegmentationMaskFolderPath) {
      if (this.isEnterpriseMode) {
        return this.handleEnterpriseImageSegmentationNext(datasetName, imageSegmentationImageFolderPath, imageSegmentationMaskFolderPath);
      }
      const {
        dataset_location,
        task_id,
      } = await rygg_createSegmentationDataset(
        imageSegmentationImageFolderPath,
        imageSegmentationMaskFolderPath,
        datasetName
      );
      await whenCeleryTaskDone(task_id);
      await this.handleDataPathUpdates([dataset_location], datasetName);
    },
    async handleEnterpriseImageSegmentationNext(datasetName, imageSegmentationImageFolderPath, imageSegmentationMaskFolderPath) {
      this.uploadStatus = "Processing...";

      try {
        const { task_id, dataset_id } = await rygg_createEnterpriseSegmentationDataset(
          imageSegmentationImageFolderPath,
          imageSegmentationMaskFolderPath,
          datasetName
        );

        await whenCeleryTaskDone(task_id, cb => this.handleUploadProgress(cb));

        const response = await rygg_getDataset(dataset_id);
        const { data: { location: path } = {} } = response;

        if (path) await this.handleDataPathUpdates([path]);
      } catch (err) {
        if (err.message) {
          this.$store.dispatch("globalView/GP_errorPopup", err.message);
        }
      } finally {
        this.uploadStatus = "";
      }
    },
    
    handleMultiModalNext(datasetName, multiModalCsvPath) {
      if (this.isEnterpriseMode) {
        return this.handleEnterpriseMultiModalNext(datasetName, multiModalCsvPath);
      }
      this.handleDataPathUpdates([multiModalCsvPath], datasetName);
    },
    async handleEnterpriseMultiModalNext(datasetName, multiModalCsvPath) {
      const file = this.multiModalCsvPath;
      this.uploadStatus = "Processing...";
      try {
        const {
          data: { task_id, dataset_id },
        } = await rygg_uploadDatasetToFileserver(file, false, this.modelType, datasetName);
        await whenCeleryTaskDone(task_id, cb => this.handleUploadProgress(cb));
        const response = await rygg_getDataset(dataset_id);
        const { data: { location: path } = {} } = response;
        if (path) await this.handleDataPathUpdates([path], datasetName);
      } catch (err) {
        if (err.message) {
          this.showErrorPopup(err.message);
        }
      } finally {
        this.uploadStatus = "";
      }
    },
    handleObjectDetectionNext(datasetName, objectDetectionCsvPath) {
      if (this.isEnterpriseMode) {
        return this.handleEnterpriseObjectDetectionNext(datasetName, objectDetectionCsvPath);
      }
      this.handleDataPathUpdates([objectDetectionCsvPath], datasetName);
    },
    async handleEnterpriseObjectDetectionNext(datasetName, objectDetectionCsvPath) {
      const file = this.objectDetectionCsvPath;
      this.uploadStatus = "Processing...";
      try {
        const {
          data: { task_id, dataset_id },
        } = await rygg_uploadDatasetToFileserver(file, false, this.modelType, datasetName);
        await whenCeleryTaskDone(task_id, cb => this.handleUploadProgress(cb));
        const response = await rygg_getDataset(dataset_id);
        const { data: { location: path } = {} } = response;
        if (path) await this.handleDataPathUpdates([path], datasetName);
      } catch (err) {
        if (err.message) {
          this.showErrorPopup(err.message);
        }
      } finally {
        this.uploadStatus = "";
      }
    },
    handleUploadProgress(uploadCb) {
      let msg = `${uploadCb.message} - ${uploadCb.so_far}%`;
      const isTaskCompleted = rygg_isTaskComplete(uploadCb.state);
      if (isTaskCompleted) {
        msg = "";
      }
      this.uploadStatus = msg;
    },
  },
};
</script>
<style lang="scss" scoped>
.main-wrapper {
  display: flex;
}

span.error {
  margin-top: 10px;
  color: red;
}
.select-type {
  &-wrapper {
    // margin: 24px 50px 0;
    background: theme-var($neutral-7);
    border-radius: 4px;
    padding: 30px;
  }
  &-contents {
    display: flex;
    justify-content: space-between;
  }
  &-item {
    width: 200px;
    height: 240px;
    padding: 15px;
    text-align: center;
    font-size: 14px;
    background: theme-var($neutral-8);
    border: 1px solid #e3e3ea;
    border-radius: 4px;
    &:not(:first-child) {
      margin-left: 15px;
    }
    &.selected,&:hover {
      background: theme-var($neutral-6);
      border: 1px solid $color-6;
    }

    & > img {
      border-radius: 4px;
    }

    & > .title {
      font-size: 16px;
      margin-top: 12px;
      margin-bottom: 10px;
    }
  }
}

.create-class {
  &-wrapper {
    width: 100%;
  }
  &-divider {
    width: 100%;
    height: 1px;
    background: theme-var($border-color);
    margin: 25px 0;
  }
  &-caption {
    display: flex;
    font-size: 16px;
    margin-bottom: 20px;

    & > img {
      margin-left: 16px;
    }
  }

  &-list-image {
    &-wrapper {
      display: flex;
    }

    width: 90px;
    height: 60px;
    border-radius: 4px;

    &:not(:first-child) {
      margin-left: 8px;
    }
  }
}

.presets-text {
  padding: 20px 20px 0;

  font-family: Nunito Sans, sans-serif;
  font-style: normal;
  font-weight: 300;
  font-size: 12px;
  line-height: 16px;
  color: #9e9e9e;
}

.model-title-input-wrapper {
  // border-bottom: 1px solid #4D556A;
}
.model-title-input {
  margin: 0px 20px 0px;
  width: calc(100% - 40px);
  height: 40px;
  line-height: 40px;
  background: transparent;
  border: 1px solid #4d556a;
  box-sizing: border-box;
  border-radius: 2px;
}

.main-file-structure-contents {
  margin: 24px 0;
  border: 1px dashed #5e6f9f;
  border-radius: 2px;
  height: 250px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
}

.action-button {
  height: 35px;
  width: 100%;

  background: #3f4c70;
  box-sizing: border-box;
  border-radius: 2px;
  // box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.25);

  font-family: Nunito Sans, sans-serif;
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 22px;

  text-align: center;

  color: #ffffff;
  &.is-disabled {
    background-color: rgb(120, 120, 120);
    cursor: not-allowed;
  }
}
.create-btn {
  background: #6185ee;
}
.mr-5 {
  margin-right: 5px;
}
.ml-5 {
  margin-left: 5px;
}
.template-image {
  width: 50%;
  height: 50%;
  margin: 0 auto;

  svg {
    display: block;
  }
}
.template-name {
  font-family: Nunito Sans, sans-serif;
  font-weight: 300;
  font-size: 12px;
  line-height: 16px;
  color: #c4c4c4;
  text-align: center;
}
.close-cross {
  position: absolute;
  right: 26px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  cursor: pointer;
  &:after {
    content: "";
    position: absolute;
    width: 18px;
    height: 2px;
    background-color: #6185ee;
    left: 50%;
    top: 50%;
    transform-origin: 50% 50%;
    transform: translate(-50%, -50%) rotate(45deg);
  }
  &:before {
    content: "";
    position: absolute;
    width: 18px;
    height: 2px;
    background-color: #6185ee;
    left: 50%;
    top: 50%;
    transform-origin: 50% 50%;
    transform: translate(-50%, -50%) rotate(-45deg);
  }
}
.plus-icon {
  vertical-align: sub;
  margin-right: 5px;
}
.template-description {
  margin: 0 20px 40px;
  font-family: Nunito Sans, sans-serif;
  font-style: normal;
  font-size: 12px;
  min-height: 15rem;
  height: 16rem;
  font-weight: normal;
  line-height: 16px;
  color: #c4c4c4;
}
.screenshoot-container {
  margin: 0 20px 20px;
  background: #23252a;
}
.template-description-else {
  min-height: 15rem;
}
.mode-path-wrapper {
  padding: 0 20px;
}
.data-partition-wrapper {
  // display: flex;
  padding-top: 20px;
  align-items: center;
  margin-bottom: 10px;
  h5 {
    font-size: 14px;
    margin-right: 10px;
    margin-bottom: 10px;
  }
}
.dataset-settings {
  display: flex;
  flex-direction: column;
  height: 100%;

  .custom-checkbox {
    display: flex;
    cursor: pointer;
  }
}

.load-contents-group {
  display: flex;
  justify-content: center;
  align-content: center;
  flex-direction: column;

  .load-dataset {
    padding: 10px;
    font-weight: 700;
    font-size: 14px;
    box-shadow: none;
  }
}

.choose-public-datasets {
  font-size: 14px;
  margin: 10px;

  a {
    text-decoration: underline;
    color: #7397fe;
    cursor: pointer;
  }
}

.footer-actions {
  padding-top: 30px;
  margin-top: auto;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  button {
    max-width: 140px;
  }
}
.default-text {
  font-family: Roboto, sans-serif;
  font-style: normal;
  font-weight: normal;
  font-size: 16px;
  line-height: 19px;
  // color: #000000;
}
.reload-dataset-btn {
  border: none;
  background: transparent;
  font-size: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  img {
    margin-right: 20px;
  }
}
.next-to-settings-btn {
  border: none;
  background: transparent;
  color: #6185ee;
  font-size: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  svg {
    margin-left: 20px;
  }
  &.disabled {
    cursor: not-allowed;
    color: rgba(#ccc, 0.7);
    svg {
      margin-left: 20px;
      path {
        fill: rgba(#ccc, 0.7);
      }
    }
  }
}
.setting-form-wrapper {
  // width: 500px !important;
  margin-top: 15px;
  .form-label {
    text-align: right;
  }
}
.normalize-inputs {
  width: 100% !important;
  height: 32px !important;
}
.normalize-button {
  height: 32px;
}
.global-training-settings {
  .popup_foot {
    padding: 0 25px 15px;
  }
}
.mr-15 {
  margin-right: 15px;
}
.customize-btn {
  background: #3f4c70;
}
.w-100 {
  width: 100%;
}
.relative {
  position: relative;
}

.find-out-message {
  font-size: 14px;
  line-height: 21px;
  margin-top: 20px;
}
.guide-link {
  cursor: pointer;
  color: $color-6;
  text-decoration: underline;
}
.image-format-message {
  margin-right: 10px;
  font-size: 14px;
}

.footer-class {
  margin-top: 30px;
}
.btn-back {
  font-size: 14px;
  line-height: 16px;
  font-weight: bold;
  color: #92929d;
}
.form_row input {
  text-align: left;
}

.form_row {
  justify-content: center;
}

.settings-layer_section > .form_row .form_label {
  flex: 0 0 40%;
  max-width: 20%;
}
.random-seed-input {
  max-width: 135px;
}
.random-seed-input-wrapper {
  // display: flex;
  // align-items: center;
  padding: 10px 0;
  justify-content: left;
  .default-text {
    margin: 0 10px 0 0;
  }
}
.cta-container {
  position: absolute;
  bottom: 30px;
  z-index: 3;
}
.mt-15 {
  margin-top: 15px;
}
.mb-15 {
  margin-bottom: 15px;
}
</style>
