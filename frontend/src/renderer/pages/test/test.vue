<template lang="pug">
  main.test-wrapper
    div.test-header
      h1.bold Evaluate    
      button.btn.btn--primary(
        v-if="testData && Object.keys(testData).length > 0"
        @click="runTest()"
      ) 
        img(src="/static/img/add-button.svg")
        | New Test
    .test-view
      div(v-if="testData && Object.keys(testData).length > 0")
        //- .toolbar
          //- .form_row
          //-   .form_label.text-right Current display
          //-   .form_input
          //-     base-select(
          //-       :select-options="testTypeOptions"
          //-       v-model="testDataset"
          //-     )
        .chart-wrapper
          template(v-for="(testTypes, key) in testData" v-if="!!testTypes")
            template(
              v-if="key === 'classification_metrics'"
            )
              template(v-for="(testFeature) in getMetricTableFeatures(testTypes)")
                metric-test-table.chart-container(
                  :testFeature="testFeature"
                  :testData="testTypes"
                  name="Classification Metrics Table"
                )
            template(v-if="key === 'segmentation_metrics'")
              template(v-for="(testFeature) in getMetricTableFeatures(testTypes)")
                metric-test-table.chart-container(
                  :testFeature="testFeature"
                  :testData="testTypes"
                  name="Segmentation Metrics Table"
                )
            template(v-if="key === 'outputs_visualization'")
              template(v-for="(testFeature, chartId) in testTypes" v-if="!!testTypes")
                div.chart-container.w-50(v-for="(feature, featureName) in testFeature")
                  chart-switch(
                    :disableHeader="false"
                    :key="key"
                    :chart-label="`${modelName(chartId) } - ${featureName} ${TestTypes[key].text}`"
                    :chart-data="feature"
                    :styles="chartStyles"
                    :chartIdx="getImageIndex(key, chartId)"
                    @chartIdxChange="handleChartIdxChange($event, key, chartId)"
                  )
            template(v-else)
              template(v-for="(testFeature, chartId) in testTypes")
                div.chart-container.w-50(
                  v-for="(feature, featureName) in testFeature"
                )
                  chart-switch(
                    v-if="key === 'confusion_matrix'"
                    :disableHeader="false"
                    :key="featureName"
                    :chart-label="`${modelName(chartId) } - ${featureName} ${TestTypes[key].text}`"
                    :chart-data="feature"
                    :styles="chartStyles"
                  )
      .no-test-view(v-else)
        p.bold There are no tests running at the moment.
        button.btn.btn--primary.run-test-button(type="button" @click="runTest()") Run Test

        .test-no-item
          .no-item-mark
            svg(xmlns='http://www.w3.org/2000/svg' width='50' height='61' viewbox='0 0 50 61' fill='none')
              path(d="M49.1058 51.3252L32.4488 24.4199V3.98337H33.9155C34.9581 3.98337 35.8035 3.13799 35.8035 2.09539V1.88798C35.8035 0.845089 34.9581 0 33.9155 0H16.0844C15.0419 0 14.1965 0.84538 14.1965 1.88798V2.09539C14.1965 3.13799 15.0419 3.98337 16.0844 3.98337H17.5512V24.4199L0.894118 51.3252C-0.245193 53.1651 -0.298794 55.389 0.751086 57.2732C1.87204 59.2856 4.0589 60.5356 6.45842 60.5356H43.5418C45.941 60.5356 48.1282 59.2856 49.2492 57.2732C50.2987 55.389 50.2451 53.1654 49.1058 51.3252ZM20.4643 25.2487V5.43991H29.536V25.2487L35.4577 34.8138H14.5423L20.4643 25.2487Z" fill="#828282")

          h3 Create Your First Test

    .test-overlay(v-if="isTestRunning")
      .spinner
        chart-spinner
      p.text-center(v-if="testStatus && testStatus[0]") {{testStatus && testStatus[0]}}
      p.text-center(v-if="testStatus && testStatus[1]") {{testStatus && testStatus[1]}}
      button.btn.btn--secondary.stop-test(@click="stopTest()") Stop Test
    test-configuration-popup(v-if="isTestConfigurationPopupOpened")
</template>

<script>
import { mapState, mapGetters } from "vuex";

import TestConfigurationPopup from "@/components/global-popups/test-configuration-popup";
import ChartSwitch from "@/components/charts/chart-switch";
import ChartSpinner from "@/components/charts/chart-spinner";
import MetricTestTable from "./components/metric-test-table";
import { TestTypes } from "@/core/constants";
import { getFirstElementFromObject } from "@/core/helpers";

const chartStyles = {
  main: {
    "min-height": "calc(50vh - 150px)"
  }
};

export default {
  components: {
    ChartSwitch,
    ChartSpinner,
    MetricTestTable,
    TestConfigurationPopup
  },
  created() {
    this.$store.dispatch("mod_webstorage/getTestStatistic").then(res => {
      this.$store.dispatch("mod_test/setTestData", res, { root: true });
    });
  },
  data() {
    return {
      chartStyles,
      testDataset: "",
      // testData: {
      //     metrics_table: [ [{
      //       categorical_accuracy: 4,
      //       top_k_categorical_accuracy: 5.4,
      //       precision: 4,
      //       recall: 5.4
      //     }],
      //     [{
      //       categorical_accuracy: 4,
      //       top_k_categorical_accuracy: 5.4,
      //       precision: 4,
      //       recall: 5.4
      //     }]]
      // },
      testTypeOptions: Object.keys(TestTypes)
        .filter(key => !TestTypes[key].disabled)
        .map(key => ({
          text: TestTypes[key].text,
          value: key
        })),
        TestTypes,
        imageChartImages: {
          outputs_visualization: { }
        }
    };
  },
  mounted() {
    if (this.testData && Object.keys(this.testData).length === 0 && this.models.length > 0) {
      this.runTest();
    }
  },
  computed: {
    ...mapGetters({
      testData: "mod_test/GET_testData",
      isTestRunning: "mod_test/GET_testRunning",
      models: "mod_workspace/GET_models",
      testStatus: "mod_test/GET_testStatus"
    }),
    ...mapState({
      isTestConfigurationPopupOpened: state =>
        state.globalView.globalPopup.showTestConfigurationPopup
    })
  },
  methods: {
    runTest() {
      this.$store.dispatch(
        "globalView/showTestConfigurationPopupAction",
        true,
        { root: true }
      );
    },
    stopTest() {
      this.$store.dispatch("mod_api/API_testStop", null, { root: true });
    },
    modelName(id) {
      return this.$store.getters["mod_workspace/GET_modelName"](id);
    },
    getMetricTableFeatures(data) {
      const chartData = getFirstElementFromObject(data);
      return chartData ? Object.keys(chartData) : [];
    },
    reset() {
      this.$store.dispatch("mod_test/reset", null, { root: true });
    },
    handleChartIdxChange(imageIdx, testName, modelId) {
      if(!this.imageChartImages[testName].hasOwnProperty(modelId)) {
        this.$set(this.imageChartImages[testName], modelId, imageIdx);
      }
      this.$set(this.imageChartImages[testName], modelId, imageIdx);
    },
    getImageIndex(testName, modelId) {
      return this.imageChartImages[testName][modelId] || 0;
    }
  }
};
</script>

<style lang="scss" scoped>

  
.test-wrapper {
  background-color: theme-var($neutral-7);
  border-radius: 15px 0px 0px 0px;
  padding: 10px 20px;
  display: flex;
  flex-direction: column;
}
.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.test-view {
  background: theme-var($neutral-8);
  border: $border-1;
  box-sizing: border-box;
  border-radius: 4px;
  height: calc(100vh - 130px);

  padding: 45px 30px;
  flex: 1;
  position: relative;
}
.chart-wrapper {
  display: flex;
  align-content: stretch;
  flex-wrap: wrap;
  margin: -10px;
}
.chart-container {
  width: calc(50% - 20px);
  margin: 10px;
}
.no-test-view {
  position: relative;
  font-size: 14px;
  height: 100%;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 1.2rem;
}
.run-test-button {
  font-size: 1.5rem;
}
.form_label {
  margin-right: 1em;
}
.form_input {
  width: 150px;
}

.test-overlay {
  position: absolute;  
	top: $h-header-win;
	right: 0;
	bottom: 0;
	left: $w-sidemenu;
	border-radius: 15px 0px 0px 0px;
	// background-color: theme-var($neutral-7);
	background-color: rgba(35, 37, 42, 100);
  z-index: 101;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  p {
    font-size: 16px;
    color: white;
  }
}
.spinner {
  position: relative;
  width: 20px;
  height: 0;
  overflow: visible;
  margin-bottom: 40px;
}

  .test-no-item {
    color: theme-var($neutral-1);
    text-align: center;

    position: absolute;  
    top: 50%; 
    left: 50%;
    transform: translate(-50%, -50%);

    & .no-item-mark {
      display: flex;
      justify-content: center;
      align-items: center;      
      margin-left: auto;
      margin-right: auto;
      width: 150px;
      height: 150px;
      border-radius: 50%;
      background: theme-var($neutral-7);
      margin-bottom: 20px;
    }
  }

</style>
