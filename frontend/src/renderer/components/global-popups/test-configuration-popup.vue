<template lang="pug">
  base-global-popup(
    :tab-set="popupTitle"
    class="test-configuration-popup"
    @closePopup="closeModal"
  )
    template(:slot="popupTitle[0] + '-content'")
      .form_row
        .form_label.text-right Test dataset:
        .form_input.flex-vertical
          base-radio(
            group-name="test-dataset"
            value-input="partitioned-dataset"
            v-model="testDataset"
          ) Use partitioned dataset
          //- base-radio(
          //-   group-name="test-dataset"
          //-   value-input="other-dataset"
          //-   v-model="testDataset"
          //-   :disabled="true"
          //- ) Use other dataset
      .form_row
        .form_label.text-right Selected model(s):
        .form_input.flex-vertical
          base-select(
            :select-multiple="true"
            :show-checkbox="true"
            :select-options="availableModels"
            v-model="selectedModels"
          )
          info-tooltip.warning
            span Select multiple models to compare
      .form_row
        .form_label.text-right Select tests:
        .form_input.checkbox-group
          base-checkbox.checkbox(
            v-for="(testType, key) in TestTypes"
            :key="key"
            v-model="testTypes[key]" 
            :disabled="!isTestAvailable(key)"
          ) {{testType.text}}
    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"  @click="closeModal") Cancel
      button.btn.btn--primary(type="button" @click="run()" :disabled="!canTestBeRun()") Run Test
</template>
<script>
import { mapState, mapGetters }         from "vuex";

import BaseGlobalPopup                  from "@/components/global-popups/base-global-popup";
import InfoTooltip                      from "@/components/different/info-tooltip.vue";
import mixinFocus                       from "@/core/mixins/net-element-settings-input-focus.js";
import { isModelValidForTest }          from '@/core/modelHelpers';
import { TestTypes }                    from '@/core/constants';
import { checkpointDirFromProject }     from '@/core/helpers.js';

export default {
  name: "GlobalTrainingSettings",
  components: { BaseGlobalPopup, InfoTooltip },
  mixins: [mixinFocus],
  data() {
    return {
      dataPath: null,
      popupTitle: ["Test Configuration"],
      testDataset: 'partitioned-dataset', // or other-dataset
      selectedModels: [],
      testTypes: {},
      TestTypes
    };
  },
  computed: {
    ...mapState({
      isModalOpened: state =>
        state.globalView.globalPopup.showGlobalTrainingSettingsPopup
    }),
    ...mapGetters({
      models: "mod_workspace/GET_models"
    }),
    settings() {
      return this.$store.getters["mod_workspace/GET_modelTrainingSetting"];
    },
    availableModels() {
      return this.models
      .filter((model) => {
        return model.networkMeta.coreStatus.Status === 'Finished' || model.networkMeta.coreStatus.Status === 'Stop';
      }).filter((model) => {
        return Object.keys(this.testTypes).every((testType) => this.testTypes[testType] === false || isModelValidForTest(model, testType))
      }).map((model) => ({
        text: model.networkName,
        value: model.networkID
      }))
    },
    checkpointFolderPaths(){
      let checkpointPaths = {}
      this.models.map(model => {
        const { apiMeta: { model_id: id, location, saved_version_location }} = model;
        checkpointPaths[id] = checkpointDirFromProject(saved_version_location || location);
      });
      return checkpointPaths;
    }
  },
  created() {
    this.testTypes = Object.keys(TestTypes).reduce((acc, key) => {
      acc[key] = TestTypes[key].default;
      return acc;
    }, {})
  },
  methods: {
    closeModal() {
      this.$store.dispatch(
        "globalView/showTestConfigurationPopupAction",
        false,
        { root: true }
      );
    },
    run() {
      const selectedTestTypes = this.getSelectedTest(this.testTypes);
      this.$store.dispatch('mod_api/API_testStart', {
        dataPath: this.dataPath,
        checkpoint_paths: this.checkpointFolderPaths,
        testTypes: selectedTestTypes,
        modelIds: this.selectedModels,
      });

      this.closeModal();
    },
    getSelectedTest(testsObj = {}) {
      const selectedTestTypes = []
      Object.keys(testsObj).forEach(key => {
        if(testsObj[key]) {
          selectedTestTypes.push(key);
        }
      });
      return selectedTestTypes
    },
    canTestBeRun() {
      const isSomeModelsSelected = this.selectedModels.length > 0;
      const isSomeTestSelected = Object.values(this.testTypes).some(x => x === true);
      return isSomeModelsSelected && isSomeTestSelected;
    },
    isTestAvailable(testType) {
      const modelIds = this.selectedModels;
      const models = this.models;

      if (TestTypes[testType].disabled) {
        this.testTypes[testType] = false;
        return false;
      }
      
      const result = !modelIds.map(modelId => {
        let model = models.find(m => m.networkID === modelId);

        return isModelValidForTest(model, testType);
      }).some(x => x === false)
      if (!result) {
        this.testTypes[testType] = false;
      }
      return result;
    }
  }
};
</script>
<style lang="scss">
@import "../../scss/base";

.normalize-inputs {
  width: 100% !important;
  height: 32px !important;
}
.test-configuration-popup {
  .settings-layer_section {
    width: 500px !important;
    padding: 25px;
  }
  .popup_foot {
    padding: 0 25px 15px;
  }
}
.text-right {
  text-align: right;
}
.flex-vertical {
  display: flex;
  flex-direction: column;
}
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
}
.checkbox {
  flex: 0 0 50%;
  margin: 5px 0;
}
.mt-5 {
  margin-top: 10px;
}
.warning {
  margin-top: 1rem;
  svg {
    cursor: default !important;
  }
}

.settings-layer_section >
.form_row .form_label {
  flex: 0 0 30%;
  max-width: 30%;
}
</style>
<!--//Epochs: 100,-->
<!--//Batch_size: 16,-->
<!--//Shuffle: true,-->
<!--//Loss: '', //[Cross-Entropy, Quadratic, Weighted Cross-Entropy, Dice]-->
<!--//LossOptions: [-->
<!--//{name: 'Cross-Entropy', value: 'Cross-Entropy'},-->
<!--//{name: 'Quadratic', value: 'Quadratic'},-->
<!--//{name: 'Weighted', value: 'Weighted'},-->
<!--//{name: 'Cross-Entropy', value: 'Cross-Entropy'},-->
<!--//{name: 'Dice', value: 'Dice'},-->
<!--//],-->
<!--//Learning_rate: 0.001,-->
<!--//Optimizer: 'ADAM', // [ADAM,SGD,Adagrad,RMSprop]-->
<!--//OptimizerOptions: [-->
<!--//{name: 'ADAM', value: 'ADAM'},-->
<!--//{name: 'SGD', value: 'SGD'},-->
<!--//{name: 'Adagrad', value: 'Adagrad'},-->
<!--//{name: 'RMSprop', value: 'RMSprop'},-->
<!--//],-->
<!--//Beta1: 0.9,-->
<!--//Beta2: 0.999,-->
<!--//Momentum: 0,-->
<!--//Centered: false,-->
