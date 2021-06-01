<template lang="pug">
.select-model-modal(:data-tutorial-target="'tutorial-create-model-new-model'")
  tempalte(v-if="!isDataWizardEnabled")
    .header
      .close-cross(@click="closeModal(true)")
      span New Model
    .main-wrapper
      .main-templates
        .main-templates-header
          h3 Templates
          //- div.search-template
          //-     img(src="./../../../../../static/img/search-models.svg")
          //-     input(type='text' placeholder="Search")
        .main-templates-items
          .template-item(
            :class="{ 'is-selected': chosenTemplate === -1 }",
            @click="choseTemplate(-1)"
          )
            .template-image
              svg(
                width="50",
                height="50",
                viewBox="-10 -10 50 50",
                fill="none",
                xmlns="http://www.w3.org/2000/svg"
              )
                rect(
                  x="0.5",
                  y="0.5",
                  width="32.3333",
                  height="32.3333",
                  rx="1.5",
                  stroke="#C4C4C4",
                  stroke-opacity="0.8"
                )
                rect(
                  x="7.16797",
                  y="7.16602",
                  width="32.3333",
                  height="32.3333",
                  rx="1.5",
                  fill="#383F50",
                  stroke="#C4C4C4"
                )
                path(
                  d="M29.79 23.9637H24.2527V29.4873H22.4298V23.9637H16.9062V22.1271H22.4298V16.6035H24.2527V22.1271H29.79V23.9637Z",
                  fill="#C4C4C4"
                )

            span.template-name Empty
          .template-item(
            v-for="(temp, i) in basicTemplates",
            :class="{ 'is-selected': chosenTemplate === i }",
            @click="choseTemplate(i)"
          )
            .template-image(v-if="temp.imgPath")
              img(:src="temp.imgPath", :alt="temp.title")
            span.template-name {{ temp.title }}
      .main-actions
        div
          h4.presets-text Name:
          .model-title-input-wrapper
            input.model-title-input(
              type="text",
              v-model="modelName",
              @keyup="onModelNameKeyup",
              :data-tutorial-target="'tutorial-create-model-model-name'"
            )
          h4.presets-text Model Path
          .mode-path-wrapper
            .form_holder
              .form_row
                input.form_input(
                  readonly,
                  type="text",
                  v-model="modelPath",
                  :data-tutorial-target="'tutorial-create-model-model-path'"
                )

                button.btn.btn--dark-blue-rev(
                  type="button",
                  @click="openFilePicker"
                ) Browse
          p.label(v-if="chosenTemplate > -1 && chosenTemplate !== null") Preview:
          .screenshoot-container(
            v-if="chosenTemplate > -1 && chosenTemplate !== null"
          )
            img.image-screenshoot(
              :src="`./../../../../../static/img/${basicTemplates[chosenTemplate].screenshoot}`"
            )
          p.label(v-if="chosenTemplate !== null") Description:
          perfect-scrollbar.template-description(
            v-if="chosenTemplate !== null",
            :data-tutorial-target="'tutorial-create-model-description'"
          )
            span(v-if="chosenTemplate > -1") {{ basicTemplates[chosenTemplate] && basicTemplates[chosenTemplate].description }}
            span(v-else) {{ 'This is an empty model which acts as a clean slate if you want to start from scratch' }}
          p.template-description-else(
            v-else,
            :data-tutorial-target="'tutorial-create-model-description'"
          )
        .main-actions-buttons
          button.action-button.mr-5(@click="closeModal(true)") Cancel
          button#create-model-btn.action-button.create-btn.ml-5(
            :class="{ 'is-disabled': isDisableCreateAction() }",
            @click="debouncedCreateModelFunction()"
          )
            svg.plus-icon(
              width="17",
              height="17",
              viewbox="0 0 17 17",
              fill="none",
              xmlns="http://www.w3.org/2000/svg"
            )
              path(
                d="M11.7924 8.82157H8.96839V11.6386H8.0387V8.82157H5.22168V7.88489H8.0387V5.06787H8.96839V7.88489H11.7924V8.82157Z",
                fill="white"
              )
              rect(
                x="0.5",
                y="0.5",
                width="16",
                height="16",
                rx="1.5",
                stroke="white"
              )
            | Create test
  template(v-else)
    .header
      .close-cross(@click="closeModal(true)")
      span {{getModalTitle}}
    .main-wrapper
      .main-file-structure-section
        template(v-if="onStep === 1")
          .main-file-structure-contents
            .load-contents-group
              button.action-button.load-dataset(
                @click="openFilePicker('setDataPath')"
                :data-tutorial-target="'tutorial-data-wizard-load-csv'"
              ) Load .CSV
          div.find-out-message Find out starting guide 
            span.guide-link(@click="openPLVideoTutorialPage") here.
        div(v-else)
          .dataset-settings(v-show="onStep === 2")
            chart-spinner(v-if="showLoadingSpinner")
            template(v-else)
              csv-table(
                v-if="dataset"
                :dataSet="dataset",
                :dataSetTypes="dataSetTypes"
                @update="handleCSVDataTypeUpdates"
              )
              span.default-text.error(v-if="isAllIOTypesFilled() && !hasInputAndTarget()") Make sure to have at least one input and one target to proceed
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
              div.footer-actions
                button.reload-dataset-btn(@click="onStep -= 1")
                  img(src='./../../../../../static/img/arrow-back.svg')
                  | Reload dataset
                div.d-flex.align-items-center
                  span.image-format-message *.jpg .png .jpeg .tiff only
                  button.next-to-settings-btn(
                    :class="{ 'disabled': isDisableCreateAction() }",
                    @click="goToTrainingSettings"
                  )
                    | Next
                    svg(width="10" height="8" viewBox="0 0 10 8" fill="none" xmlns="http://www.w3.org/2000/svg")
                      path(
                        fill-rule="evenodd"
                        clip-rule="evenodd"
                        d="M0.499999 4.00071C0.499999 3.85153 0.559263 3.70845 0.664752 3.60296C0.770241 3.49747 0.913315 3.43821 1.0625 3.43821L7.57962 3.43821L5.16425 1.02396C5.05863 0.918339 4.99929 0.775084 4.99929 0.625712C4.99929 0.476339 5.05863 0.333084 5.16425 0.227461C5.26987 0.121839 5.41313 0.0625009 5.5625 0.0625009C5.71187 0.0625009 5.85513 0.121839 5.96075 0.227462L9.33575 3.60246C9.38813 3.65471 9.42969 3.71679 9.45805 3.78512C9.48641 3.85346 9.501 3.92672 9.501 4.00071C9.501 4.0747 9.48641 4.14796 9.45805 4.2163C9.42969 4.28464 9.38813 4.34671 9.33575 4.39896L5.96075 7.77396C5.85513 7.87958 5.71187 7.93892 5.5625 7.93892C5.41313 7.93892 5.26987 7.87958 5.16425 7.77396C5.05863 7.66834 4.99929 7.52508 4.99929 7.37571C4.99929 7.22634 5.05863 7.08308 5.16425 6.97746L7.57962 4.56321L1.0625 4.56321C0.913315 4.56321 0.770241 4.50395 0.664752 4.39846C0.559263 4.29297 0.499999 4.1499 0.499999 4.00071Z"
                        fill="#6185EE"
                      )

          div.model-run-settings-page(v-show="onStep === 3")
            //h5.default-text Training settings:

            div.setting-form-wrapper.settings-layer_section
              .form_row
                .form_label
                  info-tooltip(
                    styleType="justify-content-end"
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
                    styleType="justify-content-end"
                    text="The location where your model directory will be saved."
                  ) Model Path:
                .form_input
                  input.normalize-inputs(
                    type="text",
                    v-model="modelPath",
                    :data-tutorial-target="'tutorial-create-model-model-path'"
                  )
                  button.btn.btn--dark-blue-rev.browse-path-button(
                    type="button",
                    @click="openFilePicker"
                  ) Browse
              .form_row
                .form_label
                  info-tooltip(
                    styleType="justify-content-end"
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
                    styleType="justify-content-end"
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
                    styleType="justify-content-end"
                    text="The loss function is how the error between the prediction and the labels is calculated and therefore what the models tries to optimize."
                  ) Loss:
                .form_input
                  base-select(
                    style-type='darken'
                    v-model="settings.Loss"
                    :select-options="settings.LossOptions"
                  )
              .form_row()
                .form_label
                  info-tooltip(
                    styleType="justify-content-end"
                    text="The higher the value, the quicker your model will learn. If it's too low it can easily get stuck in a poor local minima and it it's too high it can easily skip over good local minimas."
                  ) Learning rate:
                #tutorial_learning_rate.form_input
                  input.normalize-inputs(
                    type="number"
                    v-model="settings.Learning_rate")
              .form_row
                .form_label
                  span.d-flex.justify-content-end Optimizer:
                .form_input
                  base-select(
                    style-type='darken'
                    v-model="settings.Optimizer"
                    :select-options="settings.OptimizerOptions"
                  )
                  br
                  div(v-if="settings.Optimizer === 'ADAM'")
                    .form_row
                      .form_label
                        info-tooltip(
                          styleType="justify-content-end"
                          text="The exponential decay rate for the 1st moment estimates"
                        ) Beta1:
                      .form_input(data-tutorial-hover-info)
                        input.normalize-inputs(
                          type="number"
                          name="Beta1"
                          v-model="settings.Beta1")
                    .form_row
                      .form_label
                        info-tooltip(
                          styleType="justify-content-end"
                          text="The exponential decay rate for the 2nd moment estimates"
                        ) Beta2:
                      .form_input(data-tutorial-hover-info)
                        input.normalize-inputs(
                          type="number"
                          name="Beta2"
                          v-model="settings.Beta2")
                  div(v-if="settings.Optimizer === 'SGD'")
                    .form_row
                      .form_label
                        info-tooltip(
                          styleType="justify-content-end"
                          text="Accelerates the gradient descent in the relevant direction and dampens oscillations"
                        ) Momentum:
                      .form_input(data-tutorial-hover-info)
                        input.normalize-inputs(
                          type="number"
                          name="Momentum"
                          v-model="settings.Momentum")
                  div(v-if="settings.Optimizer === 'RMSprop'")
                    .form_row
                      info-tooltip(
                        styleType="justify-content-end"
                        text="Setting this to True may help with training, but is slightly more expensive in terms of computation and memory"
                      )
                        base-checkbox(v-model="settings.Centered") Centered

              .form_row
                .form_label
                .form_input
                  info-tooltip(
                    styleType="justify-content-end"
                    text="Select Yes if you want to re-shuffle the order of your dataset each epoch. Typically helps your model to generalize better."
                  )
                    base-checkbox(v-model="settings.Shuffle") Shuffle
            div.footer-actions
              button.reload-dataset-btn(@click="onStep -= 1")
                img(src='./../../../../../static/img/arrow-back.svg')
                | Edit dataset

              div.d-flex
                button.action-button.create-btn.customize-btn.mr-15(
                  @click="createModelTF2X(true)"
                ) Run&nbsp;model
                button.action-button.create-btn(
                  @click="createModelTF2X(false)"
                ) Customize




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
import {
  convertModelRecommendationToVisNodeEdgeList,
  createVisNetwork
}                                             from "@/core/helpers/layer-positioning-helper";
import { buildLayers }                        from "@/core/helpers/layer-creation-helper";

import { debounce, deepCopy, isEnvDataWizardEnabled }   from "@/core/helpers";
import cloneDeep                                        from "lodash.clonedeep";

import { doesDirExist as fileserver_doesDirExist }              from "@/core/apiFileserver";
import { getFolderContent as fileserver_getFolderContent }      from "@/core/apiFileserver";
import { getResolvedDir as fileserver_getResolvedDir }          from "@/core/apiFileserver";
import { getRootFolder as fileserver_getRootFolder }            from "@/core/apiFileserver";
import { getFileContent as fileserver_getFileContent }          from "@/core/apiFileserver";

export default {
  name: "SelectModelModal",
  components: { FilePickerPopup, CsvTable, TripleInput, InfoTooltip, ChartSpinner },
  mixins: [mixinFocus],

  data: function() {
    return {
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
        partitions: [70, 20, 10]
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
    };
  },
  computed: {
    ...mapState({
      currentProjectId: state => state.mod_project.currentProject,
      workspaces: state => state.mod_workspace.workspaceContent,
      startupDatasetPath: state => state.mod_datasetSettings.startupFolder
    }),
    ...mapGetters({
      currentProject: "mod_project/GET_project",
      projectPath: "mod_project/GET_projectPath",
      currentNetworkId: "mod_workspace/GET_currentNetworkId",
      defaultTemplate: "mod_workspace/GET_defaultNetworkTemplate",
      userEmail: "mod_user/GET_userEmail",
    }),
    isDataWizardEnabled() {
      return isEnvDataWizardEnabled();
    },
    getModalTitle() {
      switch (this.onStep){
        case 1: return 'Load your dataset'; break;
        case 2: return 'Define your dataset'; break;
        case 3: return 'Training settings'; break;
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
      getModelRecommendation: "mod_api/API_getModelRecommendation",
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

      const resolvedDir = await fileserver_getResolvedDir(this.modelPath);
      let dirContents = await fileserver_getFolderContent(resolvedDir);
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
    isDisableCreateAction() {
      if (this.isDataWizardEnabled) {
        const { modelName, csvData } = this;
        let allColumnsAreSelected = true;
        let hasInputAndTarget = true;
        if (this.isDataWizardEnabled) {
          allColumnsAreSelected = this.isAllIOTypesFilled();
          hasInputAndTarget = this.hasInputAndTarget();
        }
        return !allColumnsAreSelected || !modelName || !hasInputAndTarget;
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
    async createModelTF2X(runStatistics = false) {
      if (!this.csvData) {
        return;
      }

      const { modelName, modelPath } = this;

      // Check validity
      if (!(await this.isValidModelName(modelName))) {
        // TODO: showErrorPopup closes all popups, need to change this logic for UX
        // Annoying to have to type everything in again
        this.showErrorPopup(`The model name "${modelName}" already exists.`);
        this.setCurrentView("tutorial-model-hub-view");
        return;
      }

      if (!(await this.isValidDirName(modelName, modelPath))) {
        this.showErrorPopup(
          `The "${modelName}" folder already exists at "${modelPath}".`
        );
        this.setCurrentView("tutorial-model-hub-view");
        return;
      }

      // Creating the project/network entry in rygg
      const apiMeta = await this.createProjectModel({
        name: modelName,
        project: this.currentProjectId,
        location: `${this.modelPath}/${modelName}`
      });

      const datasetSettings = {
        randomizedPartitions: this.datasetSettings.randomizedPartitions,
        partitions: this.datasetSettings.partitions,
        featureSpecs: this.formatCSVTypesIntoKernelFormat()
      };

      const payload = {
        datasetSettings: datasetSettings,
        user_email: this.userEmail,
        model_id: apiMeta.model_id,
        skipped_workspace: runStatistics
      };

      const modelRecommendation = await this.getModelRecommendation(
        payload
      ).then(res => {
        if (typeof res === "string" && res.indexOf("Internal error") !== -1) {
          this.$store.dispatch("mod_project/deleteModel", {
            model_id: apiMeta.model_id
          });
        }
        return res;
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
      const rootPath = await fileserver_getRootFolder();
      const modelNames = modelMeta.map(x => x.name);
      if (modelNames.indexOf(modelName) !== -1) {
        this.showErrorPopup(`The model name "${modelName}" already exists.`);
        this.setCurrentView("tutorial-model-hub-view");
        return;
      }

      // TODO: test with isValidDirName
      const dirAlreadyExist = await fileserver_doesDirExist(
        `${this.modelPath}/${modelName}`
      );
      if (dirAlreadyExist) {
        this.showErrorPopup(
          `The "${modelName}" folder already exists at "${this.modelPath}".`
        );
        this.setCurrentView("tutorial-model-hub-view");
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
        this.filepickerOptions.popupTitle = "Choose data to load";
        this.filepickerOptions.filePickerType = "file";
        this.filepickerOptions.startupFolder = this.startupDatasetPath;
        this.filepickerOptions.confirmCallback = this.handleDataPathUpdates;
        this.filepickerOptions.others.showToTutotialDataFolder = true;
        this.setNextStep({ currentStep: "tutorial-data-wizard-load-csv" });
      } else {
        this.filepickerOptions.popupTitle = "Choose Model path";
        this.filepickerOptions.filePickerType = "folder";
        this.filepickerOptions.startupFolder = this.modelPath;
        this.filepickerOptions.confirmCallback = this.updateModelPath;

        this.setNextStep({ currentStep: "tutorial-create-model-model-path" });
      }
      this.showFilePickerPopup = true;
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

        this.$store.dispatch(
          "mod_datasetSettings/setStartupFolder",
          dataPath[0].match(/(.*)[\/\\]/)[1] || ""
        );

        const fileContents = await fileserver_getFileContent(
          `${dataPath[0]}`
        );

        this.dataSetTypes = await coreRequest({
          action: 'dataSelected',
          value: {
            user_email: this.userEmail,
            path: dataPath[0]
          }
        });

        if (fileContents && fileContents.file_contents) {
          this.dataset = fileContents.file_contents;
          this.datasetPath = dataPath[0];
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
    formatCSVTypesIntoKernelFormat() {
      const payload = {};

      for (const [idx, val] of this.csvData.columnNames.entries()) {
        const sanitizedVal = val.replace(/^\n|\n$/g, "");
        payload[sanitizedVal] = {
          csv_path: this.datasetPath,
          iotype: this.csvData.ioTypes[idx],
          datatype: this.csvData.dataTypes[idx],
          preprocessing: this.csvData.preprocessingTypes[idx],
        }
      }
      return payload;
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
      const dirAlreadyExist = await fileserver_doesDirExist(
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
    goToTrainingSettings() {
      if (!this.isDisableCreateAction()) {
        this.onStep += 1;
      }
    },
    openPLVideoTutorialPage() {
      window.open(PERCEPTILABS_VIDEO_TUTORIAL_URL, '_blank');
    },
  }
};
</script>
<style lang="scss" scoped>
.select-model-modal {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  min-width: 849px;
  max-width: 80vw;
}
.label {
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: normal;
  font-size: 12px;
  line-height: 16px;
  color: #e1e1e1;
  display: flex;
  align-items: center;
  padding-left: 20px;
}
.header {
  position: relative;
  height: 64px;
  display: flex;
  //justify-content: center;
  padding-left: 30px;
  align-items: center;

  background-color: rgb(20, 28, 49);
  border: 1px solid rgba(97, 133, 238, 0.4);
  border-radius: 2px 2px 0px 0px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.25);

  font-size: 14px;
  line-height: 19px;
  //text-align: center;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  color: #b6c7fb;
}
.main-wrapper {
  display: flex;
}
.main-templates {
  width: 610px;
  padding-bottom: 120px;

  background: linear-gradient(180deg, #363e51 0%, rgba(54, 62, 81, 0) 100%);
  border: 1px solid rgba(97, 133, 238, 0.4);
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
  border-radius: 0;
  min-height: 520px;
  // border-right-width: 0;
  border-bottom-left-radius: 2px;
}
.main-templates-header {
  padding: 23px 30px;
  display: flex;
  align-items: center;
  justify-content: space-around h3 {
    font-family: Nunito Sans;
    font-size: 16px;
    line-height: 22px;
    color: #e1e1e1;
  }
  .search-template {
    width: 100%;
    position: relative;
    margin-left: 140px;
    img {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      left: 12px;
    }
    input {
      width: 100%;
      border: 1px solid #4d556a;
      box-sizing: border-box;
      border-radius: 2px;
      background: transparent;
      height: 30px;
      padding-left: 42px;
    }
  }
}
.main-templates-items {
  padding: 0 30px;
  margin-top: 33px;
  display: flex;
  flex-wrap: wrap;
  justify-content: start;
}
.template-item {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  background: rgba(#383f50, 0.8);
  border-radius: 2px;
  height: 120px;
  margin-bottom: 10px;
  margin-right: 7px;
  width: calc(100% * (1 / 4) - 7.5px);
  border: 3px solid transparent;
  &:hover {
    background: rgba(#383f50, 1);
  }
  &.is-selected {
    border: 3px solid #1473e6;
    border-radius: 3px;
  }
}
.main-file-structure-section {
  box-sizing: border-box;
  width: 100%;

  background: linear-gradient(180deg, #363E51 0%, #000000 225%);
  border: 1px solid rgba(97, 133, 238, 0.4);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
  border-radius: 0 0 2px 2px;
  min-height: 320px;
}

span.error {
  margin-top: 10px;
  color: red;
}
.main-file-structure-contents {
  margin: 24px 50px 0;
  border: 1px dashed #5E6F9F;
  border-radius: 2px;
  height: 250px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
}
.main-actions {
  display: flex;
  flex-direction: column;
  width: 330px;

  background: #363e51;
  border: 1px solid rgba(97, 133, 238, 0.4);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
  border-bottom-right-radius: 2px;
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
.main-actions-buttons {
  margin-top: auto;
  padding: 20px;

  display: flex;
  justify-content: space-between;
}
.action-button {
  height: 35px;
  width: 100%;

  background: #3f4c70;
  box-sizing: border-box;
  border-radius: 2px;
  box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.25);

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
  padding: 20px 0;
  align-items: center;
  margin-bottom: 10px;
  h5 {
    font-size: 14px;
    margin-right: 10px;
    margin-bottom: 20px;
  }
}
.dataset-settings {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 30px;

  .custom-checkbox {
    display: flex;
    cursor: pointer;
  }
}

.load-contents-group {
  display: flex;
  justify-content: center;
  align-content: center;

  .load-dataset {
    padding: 10px;
    height: auto;
    background-color: #6185EE;
    font-weight: 700;
    font-size: 14px;
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
  color: #fff;
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
.model-run-settings-page {
  padding: 35px 50px 50px 50px;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.setting-form-wrapper {
  width: 330px;
  .form-label {
    text-align: right;
  }
  input {
    background-color: #202532;
    text-align: left;
    border: 1px solid #5E6F9F;
  }
}
.normalize-inputs {
  width: 100% !important;
  height: 32px !important;
}
.global-training-settings {
  .settings-layer_section {
    padding: 25px;
  }
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
.browse-path-button {
  position: absolute;
  top: 0;
  right: -90px;
  height: 32px;
  //width: 50px;
}


.find-out-message {
  margin: 20px 0 50px 50px;
  font-size: 14px;
  color: #C4C4C4;
}
.guide-link {
  cursor: pointer;
  color: #B6C7FB;
}
.image-format-message {
  margin-right: 10px;
  font-size: 14px;
  color: #fff;
}


</style>
