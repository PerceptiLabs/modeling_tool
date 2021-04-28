<template lang="pug">
  perfect-scrollbar.wrapper
    .flex
      //.box
      //  .heading Load test data
      //  .text Load the data that you want to test your model with. You can either select a full dataset, or single sample to observe the model prediction.
      //  ul(v-if="dataPath !== null")
      //    li(@click="dataPath = null") {{dataPath}}
      //  .d-flex.flex-row-reverse
      //    .d-inline-block
      //      button.btn.btn--primary(
      //        @click="loadData"
      //        type="button"
      //      ) Load
      .box
        .heading Select model
        .text Select the model you want to evaluate and run tests on. You can select several models and compare them.
        div
          ul.w-100
            li(v-for="model in models")
              .form_holder
                base-checkbox.w-100(
                  :disabled="!isModelEnabled(model)"
                  @input="onModelSelect(model)" 
                  :value="isModelChecked(model.networkID)"
                  :class="{'checkbox-disabled': !isModelEnabled(model)}"
                  )
                  span {{model.networkName}}
      .box
        .d-flex.flex-row
          div.w-50
            .heading Create test
            .text Select the model you want to evaluate and run tests on. You can select several models and compare them.
          div.w-50
            .heading Tests
            ul.w-100
              li
                .form_holder
                  base-checkbox.w-100(v-model="testTypes.confusion_matrix") Confusion matrix
              li
                .form_holder
                  base-checkbox.w-100(v-model="testTypes.metrics_table") Metrics table
        .d-flex.flex-row-reverse
          .d-inline-block
            button.btn.btn--primary(
              @click="runTest"
              type="button"
              :disabled="!canTestBeRun()"
            ) Run test
    
</template>
<script>
import {arrayIncludeOrOmit, deepCloneNetwork} from "@/core/helpers";
import { isModelValidForTest } from '@/core/modelHelpers';
import { mapGetters  } from 'vuex';

export default {
  name: 'TestCreate',
  data() {
    return {
      modelsSelectedIds: [],
      dataPath: null,
      testTypes: {
        anobia: false,
        inferobia: false,
        forward_prop: false,
        confusion_matrix: false,
        metrics_table: false,
      },
    }
  },
  watch: {
    'testTypes': {
      handler(newVal){
        this.$nextTick(() => {
          this.removeModelsIdsWhichNotMatchTestTypes()
        })
      },
      deep: true,
    },
  },
  computed:{
    ...mapGetters({
      models: 'mod_workspace/GET_models',
    }),
    modelsFolderPaths(){
      let modelsPaths = {}
      this.models.map(model => {
        const { apiMeta: { model_id: id, location, saved_version_location }} = model;
        modelsPaths[id] = saved_version_location || location;
      });
      return modelsPaths;
    }
  },
  methods: {
    isModelEnabled(model){
      let isModelEnabled = true;
      const testTypes = this.getSelectedTest(this.testTypes);
      testTypes.map(type => {
        if(!isModelValidForTest(model, type)) {
          isModelEnabled = false;
        }
      })
      return isModelEnabled;
    },
    removeModelsIdsWhichNotMatchTestTypes(){
      const modelIds = this.modelsSelectedIds;
      const models = this.models;

      modelIds.forEach(modelId => {
        let model = models.filter(m => m.networkID === modelId)[0];
        
        if(!this.isModelEnabled(model)) {
          this.onModelSelect(model);
        }
      })
    },
    loadData() {
      this.$store.dispatch('globalView/SET_filePickerPopup', {
        filePickerType: 'file',
        confirmCallback: (params) => {
          this.dataPath = params[0];
        },
        fileTypeFilter: ['csv'],
        popupTitle: 'Load test data',
        options: {
          showToTutotialDataFolder: true,
        }
      });
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
    runTest() {
      const selectedTestTypes = this.getSelectedTest(this.testTypes);
      this.$store.dispatch('mod_api/API_getTestResults', {
        dataPath: this.dataPath,
        model_paths: this.modelsFolderPaths,
        testTypes: selectedTestTypes,
        modelIds: this.modelsSelectedIds,
        });
      this.$router.push({name: 'test-dashboard'});
    },
    onModelSelect(model) {
      this.modelsSelectedIds = arrayIncludeOrOmit(this.modelsSelectedIds, model.networkID);
    },
    isModelChecked(id){
      return this.modelsSelectedIds.some(x => x === id)
    },
    canTestBeRun() {
      // const haveDataLoaded = this.dataPath !== null; // TODO was removed 
      const isSomeModelsSelected = this.modelsSelectedIds.length > 0;
      const isSomeTestSelected = Object.values(this.testTypes).some(x => x === true);
      return isSomeModelsSelected && isSomeTestSelected;
    },
  }
}
</script>
<style lang="scss" scoped>
  .wrapper {
    margin-top: 4px;
    background-color: #23252A;
    height: 100%;
    background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border: 1px solid rgba(97, 133, 238, 0.4);
    padding: 10px;
    }
  .box {
    border: 1px solid #5E6F9F;
    padding: 15px;
    margin-bottom: 10px;
    background-color:rgba( #3F4C70, 0.7)
  }
  .heading {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 20px;
  }
  .text {
    font-size: 14px;
    margin-bottom: 20px;
  }
  .checkbox-disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
</style>