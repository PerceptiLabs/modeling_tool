<template lang="pug">
div
  base-global-popup.select-model(
    :title="getModalTitle"
    titleAlign="text-center"
    @closePopup="() => closeModal(true)"
  )
    template(:slot="getModalTitle + '-content'")
      template(v-if="onStep === STEP.TYPE")
        .select-type-wrapper
          .select-type-contents
            .select-type-item(v-for="type in trainingModes" :key="type.id" @click="type.onClick")
              img(:src="type.imgPath")
              .title.bold {{type.title}}
              p.desc {{type.description}}

          div.text-center.find-out-message If you do not have your own dataset, 
            span.guide-link(@click="openPLVideoTutorialPage") click here 
            | to use a prepared dataset

      div.w-100(v-else)
        .create-class-wrapper(v-show="onStep === STEP.CLASS")
          .create-class-item(v-for="(item, idx) in classList" :key="idx")
            .create-class-divider
            .create-class-caption.bold
              | {{item.name}}
              img.btn(src="/static/img/edit.svg")
            .create-class-list-image-wrapper(v-if="item.images.length > 0")
              img.create-class-list-image(v-for="(image, idxImg) in item.images" :key="idxImg" :src="image")
            div(v-else)
              button.btn.btn--secondary(@click="onAddClassImages")
                img.icon(src="/static/img/circle-plus.svg")
                span Add Images
          .create-class-new
            .create-class-divider 
            button.btn.btn--secondary(@click="onAddClass")
              img.icon(src="/static/img/circle-plus.svg" class="svg-icon")
              span Add Class
        
        div(v-show="onStep === STEP.LOADCSV")
          .main-file-structure-contents
            .load-contents-group
              button.btn.btn--primary.load-dataset(
                @click="openFilePicker('setDataPath')"
                :data-tutorial-target="'tutorial-data-wizard-load-csv'"
              ) Upload .CSV
              p(v-if="isPublicDatasetEnabled").choose-public-datasets
                | or choose from 
                a(@click="goToPublicDatasets") Public Datasets
          div.find-out-message Find our starting guide 
            span.guide-link(@click="openPLVideoTutorialPage") here.

        .dataset-settings(v-show="onStep === STEP.PARTITION")
          chart-spinner(v-if="showLoadingSpinner")
          template(v-else)
            csv-table(
              v-if="dataset"
              :dataSet="dataset",
              :dataSetTypes="dataSetTypes"
              @update="handleCSVDataTypeUpdates"
            )
            
            data-column-option-sidebar(
                :key="index"
                v-for="index in csvData && csvData.dataTypes.length"
                :columnSelectedType="csvData && csvData.dataTypes"
                :columnNames="csvData && csvData.columnNames"
                @handleChange="updatePreprocessingTypes"
                :elementIndex="index - 1"
              )
            span.default-text.error(v-if="isAllIOTypesFilled() && !hasInputAndTarget()") Make sure to have at least one input and one target to proceed
            span.default-text.error(v-else-if="isAllIOTypesFilled() && !hasOneTarget()") Make sure to have only one target to proceed
            .data-partition-wrapper
              h5.default-text Data partition:
              triple-input(
                style-type="darken"
                v-model="datasetSettings.partitions",
                separate-sign="%",
                :validate-min="1",
                :validate-max="98",
                :validate-sum="100",
                :withLabels="true"
              )
            div(style="display:flex")
              base-checkbox(
                style="font-size: 14px; white-space:nowrap;"
                v-model="datasetSettings.randomizedPartitions"
              ) Randomize partition
              info-tooltip(
                text="Select random samples to place in each partition, good practice if your dataset is ordered"
              )
            div.randome-seed-input-wrapper.form_row
              h5.default-text Seed:
              input.random-seed-input(type="text" v-model="datasetSettings.randomSeed")
        div.d-flex.justify-content-center(v-show="onStep === STEP.TRAINING")
          template(v-if="isCreateModelLoading")
            chart-spinner(text="Building preprocessing pipelines...")
            error-cta.cta-container(v-if="isShowCTA")
          template(v-else)
            div.setting-form-wrapper.settings-layer_section
              .form_row
                .form_label
                  info-tooltip(
                    text="Model name"
                  ) Name:
                .form_input(data-tutorial-hover-info)
                  input.normalize-inputs(
                    type="text",
                    v-model="modelName",
                    @keyup="onModelNameKeyup",
                    :data-tutorial-target="'tutorial-create-model-model-name'"
                  )
              .form_row.relative
                .form_label
                  info-tooltip(
                    text="The location where your model directory will be saved."
                  ) Model Path:
                .form_input.input_group.form_row
                  input.normalize-inputs(
                    type="text" 
                    v-model="modelPath" 
                    :data-tutorial-target="'tutorial-create-model-model-path'"
                  )
                  button.btn.btn--primary.normalize-button(type="button" @click="openFilePicker") Browse
              .form_row
                .form_label
                  info-tooltip(
                    text="Number of times you want to run through the entire dataset. The more number of times, the better the model will learn you training data. Just be aware that training too long may overfit your model to your training data."
                  ) Epochs:
                #tutorial_epochs.form_input(data-tutorial-hover-info)
                  input.normalize-inputs(
                    type="number"
                    name="Epochs"
                    v-model="settings.Epochs")
              .form_row
                .form_label
                  info-tooltip(
                    text="Number of samples you want to train on at the same time. Higher value will cause the training to go quicker and may make your model generalize better. Too high value may cause your model not to learn the data well enough though."
                  ) Batch size:
                .form_input
                  input.normalize-inputs(
                    type="number"
                    name="Batch_size"
                    v-model="settings.Batch_size")
              .form_row
                .form_label
                  info-tooltip(
                    text="The loss function is how the error between the prediction and the labels is calculated and therefore what the models tries to optimize."
                  ) Loss:
                .form_input
                  base-select(
                    v-model="settings.Loss"
                    :select-options="settings.LossOptions"
                  )
              .form_row()
                .form_label
                  info-tooltip(
                    text="The higher the value, the quicker your model will learn. If it's too low it can easily get stuck in a poor local minima and it it's too high it can easily skip over good local minimas."
                  ) Learning rate:
                #tutorial_learning_rate.form_input
                  input.normalize-inputs(
                    type="number"
                    v-model="settings.Learning_rate")
              .form_row
                .form_label
                .form_input
                  base-checkbox(v-model="settings.AutoCheckpoint") Save checkpoint every epoch
              .form_row
                .form_label
                  span.d-flex Optimizer:
                .form_input
                  base-select(
                    v-model="settings.Optimizer"
                    :select-options="settings.OptimizerOptions"
                  )
              .form_row(v-if="settings.Optimizer === 'ADAM'")
                .form_label
                  info-tooltip(
                    text="The exponential decay rate for the 1st moment estimates"
                  ) Beta1:
                .form_input(data-tutorial-hover-info)
                  input.normalize-inputs(
                    type="number"
                    name="Beta1"
                    v-model="settings.Beta1")
              .form_row(v-if="settings.Optimizer === 'ADAM'")
                .form_label
                  info-tooltip(
                    text="The exponential decay rate for the 2nd moment estimates"
                  ) Beta2:
                .form_input(data-tutorial-hover-info)
                  input.normalize-inputs(
                    type="number"
                    name="Beta2"
                    v-model="settings.Beta2")
              .form_row(v-if="settings.Optimizer === 'SGD'")
                .form_label
                  info-tooltip(
                    text="Accelerates the gradient descent in the relevant direction and dampens oscillations"
                  ) Momentum:
                .form_input(data-tutorial-hover-info)
                  input.normalize-inputs(
                    type="number"
                    name="Momentum"
                    v-model="settings.Momentum")
              .form_row(v-if="settings.Optimizer === 'RMSprop'")
                .form_label
                  info-tooltip(
                    text="Setting this to True may help with training, but is slightly more expensive in terms of computation and memory")
                .form_input
                  base-checkbox(v-model="settings.Centered") Centered

              .form_row
                .form_label                  
                .form_input
                  info-tooltip(
                    text="Select Yes if you want to re-shuffle the order of your dataset each epoch. Typically helps your model to generalize better."
                  )
                    base-checkbox(v-model="settings.Shuffle") Shuffle  
        
        div(v-show="onStep === STEP.PUBLIC_LIST")
          public-datasets-list(
            @goBack="onStep = 1"
          )
    template(slot="action" v-if="onStep === STEP.CLASS")
      div.btn.btn-back(@click="gotoTypeStep")
        img.icon(src="/static/img/back.svg")
        span Back
      button.btn.btn--primary(@click="gotoTrainingSettings" :class="{'btn--disabled' : isDisableCreateAction() }")
        span Next
        img.icon.rotate-180(src="/static/img/back.svg")
    
    template(slot="action" v-if="onStep === STEP.PARTITION && !showLoadingSpinner")
      button.link.reload-dataset-btn(@click="toPrevStep")
        img(src='/static/img/back-arrow.svg')
        | Reload dataset
      div.d-flex.align-items-center
        div.image-format-message *.jpg .png .jpeg .tiff only
        button.btn.btn--primary(
          :class="{ 'btn--disabled': isDisableCreateAction() }",
          :disabled="isDisableCreateAction()"
          @click="gotoTrainingSettings"
        )
          | Next
          svg(width="10" height="8" viewBox="0 0 10 8" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M0.499999 4.00071C0.499999 3.85153 0.559263 3.70845 0.664752 3.60296C0.770241 3.49747 0.913315 3.43821 1.0625 3.43821L7.57962 3.43821L5.16425 1.02396C5.05863 0.918339 4.99929 0.775084 4.99929 0.625712C4.99929 0.476339 5.05863 0.333084 5.16425 0.227461C5.26987 0.121839 5.41313 0.0625009 5.5625 0.0625009C5.71187 0.0625009 5.85513 0.121839 5.96075 0.227462L9.33575 3.60246C9.38813 3.65471 9.42969 3.71679 9.45805 3.78512C9.48641 3.85346 9.501 3.92672 9.501 4.00071C9.501 4.0747 9.48641 4.14796 9.45805 4.2163C9.42969 4.28464 9.38813 4.34671 9.33575 4.39896L5.96075 7.77396C5.85513 7.87958 5.71187 7.93892 5.5625 7.93892C5.41313 7.93892 5.26987 7.87958 5.16425 7.77396C5.05863 7.66834 4.99929 7.52508 4.99929 7.37571C4.99929 7.22634 5.05863 7.08308 5.16425 6.97746L7.57962 4.56321L1.0625 4.56321C0.913315 4.56321 0.770241 4.50395 0.664752 4.39846C0.559263 4.29297 0.499999 4.1499 0.499999 4.00071Z"
            )       
    template(slot="action" v-if="onStep === STEP.TRAINING && !isCreateModelLoading")
      div.btn.btn-back(@click="toPrevStep")
        img.icon(src="/static/img/back.svg")
        span Back
      div.d-flex
        button.btn.btn--secondary.mr-15(
          @click="createModelTF2X(true)"
        ) Run model
        button.btn.btn--primary(
          @click="createModelTF2X(false)"
        ) Customize
    template(slot="action" v-if="onStep === STEP.PUBLIC_LIST")
    template(v-else)
      | Error


  file-picker-popup(
    v-if="showFilePickerPopup",
    :popupTitle="filepickerOptions.popupTitle",
    :filePickerType="filepickerOptions.filePickerType",
    :startupFolder="filepickerOptions.startupFolder",
    :confirmCallback="filepickerOptions.confirmCallback",
    :cancelCallback="closePopup"
    :options="filepickerOptions.others"
  )
</template>
<script>
import { coreRequest }                        from "@/core/apiWeb.js";
import imageClassification                    from "@/core/basic-template/image-classification.js";
import reinforcementLearning                  from "@/core/basic-template/reinforcement-learning.js";
import linearRegression                       from "@/core/basic-template/linear-regression.js";
import objectDetection                        from "@/core/basic-template/object-detection.js";
import ganTemplate                            from "@/core/basic-template/gan-template.js";
import FilePickerPopup                        from "@/components/global-popups/file-picker-popup.vue";
import CsvTable                               from "@/components/different/csv-table.vue";
import TripleInput                            from "@/components/base/triple-input";
import InfoTooltip                            from "@/components/different/info-tooltip.vue";
import ChartSpinner                           from "@/components/charts/chart-spinner";
import {defaultTrainingSettings, PERCEPTILABS_VIDEO_TUTORIAL_URL} from "@/core/constants";
import { mapActions, mapState, mapGetters }   from "vuex";
import mixinFocus                             from "@/core/mixins/net-element-settings-input-focus.js";
import DataColumnOptionSidebar                from '@/components/different/data-column-option-sidebar';
import ErrorCta                               from '@/components/error-cta';
import {
  convertModelRecommendationToVisNodeEdgeList,
  createVisNetwork
}                                             from "@/core/helpers/layer-positioning-helper";
import { buildLayers }                        from "@/core/helpers/layer-creation-helper";
import BaseGlobalPopup                        from "@/components/global-popups/base-global-popup";

import { debounce, deepCopy, isEnvDataWizardEnabled, isPublicDatasetEnabled }   from "@/core/helpers";
import cloneDeep                                        from "lodash.clonedeep";

import { doesDirExist as rygg_doesDirExist }              from "@/core/apiRygg";
import { getFolderContent as rygg_getFolderContent }      from "@/core/apiRygg";
import { getResolvedDir as rygg_getResolvedDir }          from "@/core/apiRygg";
import { getRootFolder as rygg_getRootFolder }            from "@/core/apiRygg";
import { getFileContent as rygg_getFileContent }          from "@/core/apiRygg";
import { loadDataset  as rygg_createDataset }             from "@/core/apiRygg";
import { getDatasets  as rygg_getDataset }                from "@/core/apiRygg";
import { uploadFile as rygg_uploadFile }                  from "@/core/apiRygg";
import { getFile as rygg_getFile }                        from "@/core/apiRygg";
import { renderingKernel }              from "@/core/apiRenderingKernel";
import { formatCSVTypesIntoKernelFormat } from "@/core/helpers/model-helper";
import { ENTERPRISE_DATASET_FOLDER_PREFIX } from '@/core/constants.js';

import PublicDatasetsList from './public-datasets-list.vue'

const STEP = {
  LOADCSV: 1,
  PARTITION: 2,
  TRAINING: 3,  
  PUBLIC_LIST: 4,  
  TYPE: 5,
  CLASS: 6,
}

const mockClassList = [
  {
    id: 1,
    name: 'Class 1',
    images: [
      '/static/img/project-page/classification.png',
      '/static/img/project-page/linear-regression.png'
    ]
  },
  {
    id: 2,
    name: 'Class 2',
    images: []
  }
]

export default {
  name: "SelectModelModal",
  components: { BaseGlobalPopup, FilePickerPopup, CsvTable, TripleInput, InfoTooltip, ChartSpinner, DataColumnOptionSidebar, PublicDatasetsList },
  mixins: [mixinFocus],
  async created() {
    const showNewModelPopup = this.showNewModelPopup;
    if(typeof showNewModelPopup === 'object' && showNewModelPopup !== null &&  showNewModelPopup.hasOwnProperty('datasetId')) {
      let datasetPath = '';
      const allDatasets = this.$store.getters['mod_datasets/GET_datasets'];
      allDatasets.forEach(dataset => {
        if(dataset.dataset_id === showNewModelPopup.datasetId) {
           datasetPath = dataset.location;
        }
      })
      this.handleDataPathUpdates([datasetPath]);
    }
  },
  data: function() {
    return {
      STEP : STEP,
      trainingModes: [
        {
          id: 1,
          title: "Image Classification",
          description: "Train your model to classify images",          
          imgPath: "./static/img/project-page/upload-class.jpg",
          onClick: this.gotoClassStep,
        },
        {
          id: 2,
          title: "Segment Images",
          description: "Train your model to segment things in images",          
          imgPath: "./static/img/project-page/upload-segment.jpg",
          onClick: () => {},
        },
        {
          id: 3,
          title: "Multi-Modal",
          description: "Combined data types, inputs and targets for more complex problems",          
          imgPath: "./static/img/project-page/upload-multi.jpg",
          onClick: () => {},
        }
      ],
      classList: mockClassList,
      basicTemplates: [
        {
          title: "Image Classification CNN",
          imgPath: "./static/img/project-page/classification.png",
          template: imageClassification,
          description:
            "This is a simple image classification template, perfect for datasets such as MNIST. The standard dataset included with this template is an MNIST dataset where the input is an array of 784 grayscale pixel values and 10 unique label values (integers 0-9). The model consists of a reshaping component, a convolutional layer, and a fully connected output layer with 10 neurons. Because of the reshaping component it requries the input data to be 784 or a form thereof (28x28, for example). The labels must be integers ranging from 0 to 9 to be compatible with the one hot encoding that is applied to the labels.",
          screenshoot: "template_image_classification.png"
        },
        {
          title: "Linear Regression",
          imgPath: "./static/img/project-page/linear-regression.png",
          template: linearRegression,
          description: `This is a template for linear regression, where it tries to create a line of best fit for the datapoints you load. The standard dataset is a one-dimensional input value and one-dimensional labels. The input data can be multidimensional, but our visualizations will display the data in one dimension. The labels data must be one-dimensional as they represent the value of the input data. The model is built as a single fully connected layer with one neuron as output.`,
          screenshoot: "template_linear_regression.png"
        },
        {
          title: "DQN",
          imgPath: "./static/img/project-page/reinforcement-learning.png",
          template: reinforcementLearning,
          description: `This is a template for Reinforcement Learning consisting of one grayscale component, one convolutional layer and one fully connected layer as output. This template uses Q learning on Atari Gym games, where it is set up to play breakout. To play another game, you will change the neurons in the fully connected layer to match the number of possible actions in the actionspace, which you can see in the Environment component.`,
          screenshoot: "template_dqn.png"
        },
        {
          title: "YOLO V1",
          imgPath: "./static/img/project-page/object-detection.png",
          template: objectDetection,
          description: `This is a template of the Object Detection model YOLO. It trains on a custom-built dataset containing different shapes as standard. Since it consists of only convolutional layers, any input data will work to train on, as long as the label data matches the input data.`,
          screenshoot: "template_yolo.png"
        },
        {
          title: "GAN",
          imgPath: "./static/img/project-page/GAN.png",
          template: ganTemplate,
          description: `This is a template for a Generative Adversarial Network (GAN) where it trains on the MNIST data as a standard. The model consists of a generative network and a discriminative network, as well as a switch layer which switches between the generated image and real image.`,
          screenshoot: "template_gan.png"
        }
      ],
      chosenTemplate: null,
      modelName: "",
      description: "",
      modelPath: "",
      showFilePickerPopup: false,
      hasChangedModelName: false,
      csvData: null, // parsed dataset and meta
      dataset: null,
      datasetPath: null,
      dataSetTypes: [],
      datasetSettings: {
        randomizedPartitions: true,
        partitions: [70, 20, 10],
        randomSeed: '123',
      },
      filepickerOptions: {
        popupTitle: "",
        filePickerType: "",
        startupFolder: "",
        confirmCallback: "",
        others: {}
      },
      debouncedCreateModelFunction: null,
      onStep: 1,
      settings: defaultTrainingSettings,
      showLoadingSpinner: false,
      isCreateModelLoading: false,
      createdFromDatasetId: null,
      isShowCTA: false,
      createdFromDatasetId: null,
    };
  },
  computed: {
    ...mapState({
      currentProjectId: state => state.mod_project.currentProject,
      workspaces: state => state.mod_workspace.workspaceContent,
      startupDatasetPath: state => state.mod_datasetSettings.startupFolder,
      showNewModelPopup:    state => state.globalView.globalPopup.showNewModelPopup,
    }),
    ...mapGetters({
      currentProject: "mod_project/GET_project",
      projectPath: "mod_project/GET_projectPath",
      currentNetworkId: "mod_workspace/GET_currentNetworkId",
      defaultTemplate: "mod_workspace/GET_defaultNetworkTemplate",
      userEmail: "mod_user/GET_userEmail",
      isEnterpriseMode:     'globalView/get_isEnterpriseApp',
    }),
    isPublicDatasetEnabled() {
      return isPublicDatasetEnabled();
    },
    isDataWizardEnabled() {
      return isEnvDataWizardEnabled();
    },
    getModalTitle() {
      switch (this.onStep){
        case STEP.LOADCSV: return 'Load your dataset'; break;
        case STEP.PARTITION: return 'Define your dataset'; break;
        case STEP.TRAINING: return 'Training settings'; break;
        case STEP.PUBLIC_LIST: return 'Load dataset'; break;
        case STEP.TYPE: return 'What do you want to do?'; break;
        case STEP.CLASS: return 'Add one class for each type of image you want to tell apart.'; break;        
      }
    }

  },
  mounted() {
    this.modelPath = this.projectPath;
    document.addEventListener("keyup", this.handleKeyup);

    this.debouncedCreateModelFunction = debounce(_ => {
      this.createModel();
    }, 1000);

    if (this.isDataWizardEnabled) {
      this.setCurrentView("data-wizard-onboarding");
    } else {
      this.setCurrentView("tutorial-create-model-view");
    }
  },
  beforeDestroy() {
    document.removeEventListener("keyup", this.handleKeyup);
  },
  methods: {
    ...mapActions({
      addNetwork: "mod_workspace/ADD_network",
      closeStatsTestViews: "mod_workspace/SET_statisticsAndTestToClosed",
      createProjectModel: "mod_project/createProjectModel",
      getModelMeta: "mod_project/getModel",
      getProjects: "mod_project/getProjects",
      showErrorPopup: "globalView/GP_errorPopup",
      setCurrentView: "mod_tutorials/setCurrentView",
      setNextStep: "mod_tutorials/setNextStep",
      activateNotification: "mod_tutorials/activateNotification",
      setChecklistItemComplete: "mod_tutorials/setChecklistItemComplete",
    }),
    closeModal(triggerViewChange = false) {
      this.$store.dispatch("globalView/SET_newModelPopup", false);

      if (triggerViewChange) {
        this.setCurrentView("tutorial-model-hub-view");
      }
    },
    choseTemplate(index) {
      this.chosenTemplate = index;
      this.autoPopulateName();

      this.setNextStep({ currentStep: "tutorial-create-model-new-model" });
    },
    async autoPopulateName() {
      if (this.modelName && this.hasChangedModelName) {
        return;
      }
      if (!this.modelPath) {
        return;
      }

      const resolvedDir = await rygg_getResolvedDir(this.modelPath);
      let dirContents = await rygg_getFolderContent(resolvedDir);
      // In case that  default PL folder doesn't exist dirs will be empty sting.
      if(typeof dirContents.dirs === 'string') {
        dirContents.dirs = [];
      }
      let namePrefix = "";
      if (
        this.chosenTemplate && // null case for TF2X models
        this.chosenTemplate >= 0 &&
        this.chosenTemplate <= this.basicTemplates.length - 1
      ) {
        namePrefix = this.basicTemplates[this.chosenTemplate].title.replace(
          " ",
          ""
        );
      } else {
        namePrefix = "Model";
      }

      console.log("autoPopulateName3")
      const highestSuffix = dirContents.dirs
        .filter(d => d.startsWith(namePrefix))
        .map(d => d.replace(`${namePrefix} `, ""))
        .map(d => parseInt(d))
        .filter(suffixNum => !isNaN(suffixNum))
        .reduce((max, curr) => Math.max(max, curr), 0);
      this.modelName = `${namePrefix} ${highestSuffix + 1}`;
    },
    isAllIOTypesFilled() {
      if (this.isDataWizardEnabled) {
        const { csvData } = this;
        return (
          csvData &&
          csvData.ioTypes.filter(v => v !== undefined).length ===
          csvData.ioTypes.length
        );
      } else {
        return false;
      }
    },
    hasInputAndTarget() {
      if (this.isDataWizardEnabled) {
        const { csvData } = this;
        return (
          csvData &&
          csvData.ioTypes.filter(v => v === "Input").length > 0 &&
          csvData.ioTypes.filter(v => v === "Target").length > 0
        );
      } else {
        return false;
      }
    },
    hasOneTarget() {
      if (this.isDataWizardEnabled) {
        const { csvData } = this;
        return (
          csvData &&
          csvData.ioTypes.filter(v => v === "Target").length === 1
        );
      } else {
        return false;
      }
    },
    isDisableCreateAction() {
      if (this.isDataWizardEnabled) {
        const { modelName, csvData } = this;
        let allColumnsAreSelected = true;
        let hasInputAndTarget = true;
        let hasOneTarget = true;
        if (this.isDataWizardEnabled) {
          allColumnsAreSelected = this.isAllIOTypesFilled();
          hasInputAndTarget = this.hasInputAndTarget();
          hasOneTarget = this.hasOneTarget();
        }
        return !allColumnsAreSelected || !hasInputAndTarget || !hasOneTarget;
      } else {
        const { chosenTemplate, modelName, basicTemplates } = this;
        return chosenTemplate === null || !modelName;
      }
    },
    async createModel() {
      if (this.isDataWizardEnabled) {
        await this.createModelTF2X();
      } else {
        await this.createModelTF1X();
      }
    },
    deleteModelWithErrorPopup(modelId, errorMessage) {
      this.$store.dispatch("mod_project/deleteModel", {
        model_id: modelId
      });
      this.showErrorPopup(errorMessage);
      this.isCreateModelLoading = false;
    },
    async createModelTF2X(runStatistics = false) {
      if (!this.csvData) {
        return;
      }
      this.isCreateModelLoading = true;
      const { modelName, modelPath } = this;

      this.isShowCTA = false;
      const timerId = setTimeout(() => {
        this.isShowCTA = true;
      }, 3 * 60 * 1000);
      
      // Check validity
      if (!(await this.isValidModelName(modelName))) {
        // TODO: showErrorPopup closes all popups, need to change this logic for UX
        // Annoying to have to type everything in again
        this.showErrorPopup(`The model name "${modelName}" already exists.`);
        this.isCreateModelLoading = false;
        return;
      }

      if (!(await this.isValidDirName(modelName, modelPath))) {
        this.showErrorPopup(
          `The "${modelName}" folder already exists at "${modelPath}".`
        );
        this.isCreateModelLoading = false;
        return;
      }

      // Creating the project/network entry in rygg
      const apiMeta = await this.createProjectModel({
        name: modelName,
        project: this.currentProjectId,
        location: `${this.modelPath}/${modelName}`,
        datasets: [this.createdFromDatasetId],
      });

      const datasetSettings = {
        randomizedPartitions: this.datasetSettings.randomizedPartitions,
        partitions: this.datasetSettings.partitions,
        featureSpecs: formatCSVTypesIntoKernelFormat(this.csvData),
        filePath: this.datasetPath,
        randomSeed: this.datasetSettings.randomSeed
      };
      const userEmail = this.userEmail;
      
      await renderingKernel.waitForDataReady(datasetSettings, userEmail);
        
      const modelRecommendation = await renderingKernel.getModelRecommendation(
        datasetSettings,
        this.userEmail,
        apiMeta.model_id,
        runStatistics
      )   
      .then(res => {
        if ("errorMessage" in res) {
          this.deleteModelWithErrorPopup(
            apiMeta.model_id,
            "Couldn't get model recommendation because the Kernel responded with an error: " + res["errorMessage"]
          );
        }
        return res;
      })
     .catch(err => {
       this.deleteModelWithErrorPopup(
         apiMeta.model_id,
         "Couldn't get model recommendation due to an exception: " + err
       );
      });         
        
      const inputData = convertModelRecommendationToVisNodeEdgeList(
        modelRecommendation
      );
      const network = createVisNetwork(inputData);

      // Wait till the 'stabilized' event has fired
      await new Promise(resolve =>
        network.on("stabilized", async data => resolve())
      );

      // Creating the networkElementList for the network
      var ids = inputData.nodes.getIds();
      var nodePositions = network.getPositions(ids);
      const layers = await buildLayers(modelRecommendation, nodePositions);

      // Creating network and adding the prepped layer to it
      const newNetwork = cloneDeep(this.defaultTemplate);
      newNetwork.networkID = apiMeta.model_id;
      newNetwork.networkName = modelName;
      newNetwork.networkElementList = layers;
      newNetwork.networkMeta.datasetSettings = deepCopy(datasetSettings);
      // Adding network to workspace
      newNetwork.networkMeta.trainingSettings = deepCopy(this.settings);
      await this.$store.dispatch('mod_workspace/setViewType', 'model');
      await this.addNetwork({ network: newNetwork, apiMeta }).then(() => {
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
        { networkId: this.currentNetworkId }
      );
      await this.$store.dispatch(
        "mod_workspace/SET_currentModelIndexByNetworkId",
        apiMeta.model_id
      );
      await this.$store.dispatch("mod_workspace/setViewType", "model");

      this.$store.commit("mod_empty-navigation/set_emptyScreenMode", 0);
      this.setChecklistItemComplete({ itemId: "createModel" });

      this.$nextTick(() => {
        this.setCurrentView("tutorial-workspace-view");
      });
      this.isCreateModelLoading = false;
      this.closeModal(false);
    },
    async createModelTF1X() {
      const { chosenTemplate, modelName, basicTemplates } = this;
      if (chosenTemplate === null || !modelName) return;

      // TODO: test with isValidModelName
      // check if models name already exists
      const promiseArray = this.currentProject.models.map(x =>
        this.getModelMeta(x)
      );
      const modelMeta = await Promise.all(promiseArray);
      const rootPath = await rygg_getRootFolder();
      const modelNames = modelMeta.map(x => x.name);
      if (modelNames.indexOf(modelName) !== -1) {
        this.showErrorPopup(`The model name "${modelName}" already exists.`);
        this.isCreateModelLoading = false;
        return;
      }

      // TODO: test with isValidDirName
      const dirAlreadyExist = await rygg_doesDirExist(
        `${this.modelPath}/${modelName}`
      );
      if (dirAlreadyExist) {
        this.showErrorPopup(
          `The "${modelName}" folder already exists at "${this.modelPath}".`
        );
        this.isCreateModelLoading = false;
        return;
      }

      let modelType;
      let newModelId;

      this.createProjectModel({
        name: modelName,
        project: this.currentProjectId,
        location: `${this.modelPath}/${modelName}`
      })
        .then(apiMeta => {
          newModelId = apiMeta.model_id;

          if (chosenTemplate === -1) {
            const defaultTemplate = cloneDeep(this.defaultTemplate);
            defaultTemplate.networkID = apiMeta.model_id;
            defaultTemplate.networkName = modelName;

            modelType = "Custom";

            return this.addNetwork({ network: defaultTemplate, apiMeta });
          } else {
            let template = cloneDeep(
              basicTemplates[chosenTemplate].template.network
            );

            const newRootPath = rootPath.replace(/\\/g, "/");
            this.convertToAbsolutePath(
              template.networkElementList,
              newRootPath
            );
            template.networkName = modelName;
            template.networkID = apiMeta.model_id;

            modelType = basicTemplates[chosenTemplate].title;

            return this.addNetwork({ network: template, apiMeta });
          }
        })
        .then(_ => {
          this.getProjects();
          this.$store.dispatch("mod_tracker/EVENT_modelCreation", modelType, {
            root: true
          });

          this.closeStatsTestViews({ networkId: this.currentNetworkId });

          this.$store.dispatch(
            "mod_workspace/SET_currentModelIndexByNetworkId",
            newModelId
          );
          this.$store.dispatch("mod_workspace/setViewType", "model");

          this.$store.commit("mod_empty-navigation/set_emptyScreenMode", 0);
          this.setChecklistItemComplete({ itemId: "createModel" });

          // closing model will invoke:
          // setCurrentView('tutorial-model-hub-view');
          // hence the next tick
          this.$nextTick(() => {
            this.setCurrentView("tutorial-workspace-view");
          });

          this.closeModal(false);
        });
    },
    openFilePicker(openFilePickerReason) {
      if (openFilePickerReason === "setDataPath") {
        if (this.isEnterpriseMode) {
          this.loadDataset();
        } else {
          this.filepickerOptions.popupTitle = "Choose data to load";
          this.filepickerOptions.filePickerType = "file";
          this.filepickerOptions.startupFolder = this.startupDatasetPath;
          this.filepickerOptions.confirmCallback = this.handleDataPathUpdates;
          this.filepickerOptions.others.showToTutotialDataFolder = true;
          this.setNextStep({ currentStep: "tutorial-data-wizard-load-csv" });
          this.showFilePickerPopup = true;
        }
        
      } else {
        this.filepickerOptions.popupTitle = "Choose Model path";
        this.filepickerOptions.filePickerType = "folder";
        this.filepickerOptions.startupFolder = this.modelPath;
        this.filepickerOptions.confirmCallback = this.updateModelPath;
        this.showFilePickerPopup = true;
        this.setNextStep({ currentStep: "tutorial-create-model-model-path" });
      }
    
    },
    closePopup() {
      this.showFilePickerPopup = false;
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
      this.showFilePickerPopup = false;
    },
    convertToAbsolutePath(elementList, rootPath) {
      const suffix = "/";

      for (var el in elementList) {
        if (
          elementList[el].layerType === "Data" &&
          elementList[el].layerSettings.accessProperties &&
          elementList[el].layerSettings.accessProperties.Sources
        ) {
          if (elementList[el].layerSettings.accessProperties.Sources.length) {
            elementList[el].layerSettings.accessProperties.Sources.forEach(
              item => {
                item.path =
                  rootPath + suffix + "tutorial_data" + suffix + item.path;
              }
            );
          }
        }
      }
    },
    handleKeyup(event) {
      if (event.key === "Escape") {
        event.stopPropagation();
        if (this.showFilePickerPopup) {
          this.showFilePickerPopup = false;
        } else {
          this.closeModal(true);
        }
      } else if (event.key === "Enter" && !this.isDisableCreateAction()) {
        // event.stopPropagation();
        // this.debouncedCreateModelFunction();
        // this.chosenTemplate = null;
        // this.modelName = "";
      }
    },
    onModelNameKeyup() {
      if (this.modelName === "") {
        this.hasChangedModelName = false;
      } else {
        this.hasChangedModelName = true;
      }

      this.setNextStep({ currentStep: "tutorial-create-model-model-name" });
    },
    async handleDataPathUpdates(dataPath) {
      if (!dataPath || !dataPath.length || !dataPath[0]) {
        this.showFilePickerPopup = false;
        return;
      }

      try {
        this.showLoadingSpinner = true;
        this.showFilePickerPopup = false;
        this.toNextStep();
        if(this.isEnterpriseMode) {
          this.$store.dispatch("mod_datasetSettings/setStartupFolder", ENTERPRISE_DATASET_FOLDER_PREFIX);
        } else {
          this.$store.dispatch(
          "mod_datasetSettings/setStartupFolder",
          dataPath[0].match(/(.*)[\/\\]/)[1] || ""
        );
        }
        
        
        // create Dataset or User existing one
        await this.$store.dispatch('mod_datasets/getDatasets');
        const allDatasets = this.$store.getters['mod_datasets/GET_datasets'];
        const datasetIndex = allDatasets.map(x => x.location).indexOf(dataPath[0]);
        if (datasetIndex !== -1) {
          console.log(allDatasets[datasetIndex].dataset_id);
          this.createdFromDatasetId = allDatasets[datasetIndex].dataset_id;
        } else {
          const createDataset = await rygg_createDataset({
            project: 1,
            name: dataPath[0],
            location: dataPath[0],
          });
          this.$store.dispatch('mod_datasets/getDatasets');
          this.createdFromDatasetId = createDataset.data.dataset_id;
        } 
        
        const getFileContentPath = this.isEnterpriseMode ? `${ENTERPRISE_DATASET_FOLDER_PREFIX}${dataPath[0]}` : dataPath[0]
        const fileContents = await rygg_getFileContent(getFileContentPath);

        this.dataSetTypes = await renderingKernel.getDataTypes(getFileContentPath, this.userEmail)
        .then(res => {
          if ("errorMessage" in res) {
            this.showErrorPopup(
              "Couldn't get data types because the Kernel responded with an error: " + res["errorMessage"]
            );
            this.showLoadingSpinner = false;
          }
          return res;
        })
        .catch(err => {  
          console.error(err);         
          this.showErrorPopup("Error: Couldn't infer data types due to an exception: " + err);
          this.showLoadingSpinner = false;
        });           

        if (fileContents && fileContents.file_contents) {
          this.dataset = fileContents.file_contents;
          this.datasetPath = getFileContentPath;
          this.autoPopulateName();
        }
      } catch (e) {
        this.showFilePickerPopup = true;
        this.toPrevStep()
      }
      finally {
        this.showLoadingSpinner = false;
      }

      this.activateNotification();
    },
    handleCSVDataTypeUpdates(payload) {
      this.csvData = payload;
    },
    async isValidModelName(modelName) {
      if (!modelName) {
        return;
      }

      const promiseArray = this.currentProject.models.map(x =>
        this.getModelMeta(x)
      );
      const modelMeta = await Promise.all(promiseArray);
      const modelNames = modelMeta.map(x => x.name);

      // Making sure name is not already in the list
      return modelNames.indexOf(modelName) === -1;
    },
    async isValidDirName(modelName, modelPath) {
      const dirAlreadyExist = await rygg_doesDirExist(
        `${modelPath}/${modelName}`
      );

      return !dirAlreadyExist;
    },
    toNextStep() {
      this.onStep += 1;
    },
    toPrevStep() {
      this.onStep -= 1;
    },    
    gotoTypeStep() {
      this.onStep = STEP.TYPE;
    },
    gotoClassStep() {
      this.onStep = STEP.CLASS;
    },    
    goToPublicDatasets() {
      this.onStep = STEP.PUBLIC_LIST;
    },
    gotoTrainingSettings() {
      // if (!this.isDisableCreateAction()) 
      {
        this.onStep = STEP.TRAINING;
      }
    },
    openPLVideoTutorialPage() {
      window.open(PERCEPTILABS_VIDEO_TUTORIAL_URL, '_blank');
    },
    updatePreprocessingTypes(numColumn, value){
      this.csvData.preprocessingTypes.splice(numColumn, 1, value);
    },
    onAddClass() {
      this.classList.push({
        id: this.classList.length + 1,
        name: 'Class ' + (this.classList.length + 1),
        images: []
      })
    },
    onAddClassImages(){

    },
    loadDataset() {
        const fileInput = document.createElement('input');
        fileInput.setAttribute('type', 'file');
        fileInput.setAttribute('accept', '.csv,.zip');
        fileInput.addEventListener('change', (e) => {
          const file = e.target.files[0];
          const location = `${ENTERPRISE_DATASET_FOLDER_PREFIX}${file.name}`;
          rygg_uploadFile(file, false)
            .then(async () => {
              this.handleDataPathUpdates([file.name]);
            })
            .catch(async (e) => {
              if (e.response.data === `File ${file.name} exists and overwrite is false`) {
                this.handleDataPathUpdates([file.name]);

              }
            })
        })
        fileInput.click();
      },
  }
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
    border: 1px solid #E3E3EA;
    border-radius: 4px;
    &:not(:first-child) {
      margin-left: 15px;
    }
    &:hover {
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
  border: 1px dashed #5E6F9F;
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
    color: #7397FE;
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
  color: #92929D;
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
.randome-seed-input-wrapper {
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
</style>
