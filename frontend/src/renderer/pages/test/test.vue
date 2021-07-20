<template lang="pug">
  main.test-wrapper
    h1.test-header Test
    .test-view
      div(v-if="testData && Object.keys(testData).length > 0")
        .toolbar
          //- .form_row
          //-   .form_label.text-right Current display
          //-   .form_input
          //-     base-select(
          //-       :select-options="testTypeOptions"
          //-       v-model="testDataset"
          //-     )
          button.btn.btn--primary.new-test(@click="runTest()") + New Test
        .chart-wrapper
          template(v-for="(testTypes, key) in testData" v-if="!!testTypes")
            template(
              v-if="key === 'metrics_table'"
            )
              template(v-for="(testFeature) in getMetricTableFeatures(testTypes)")
                metric-test-table.chart-container(
                  :testFeature="testFeature"
                  :testData="testTypes"
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
        p There are no tests running at the moment.
        button.btn.btn--primary.run-test-button(type="button" @click="runTest()") Run Test
    .test-overlay(v-if="isTestRunning")
      .spinner
        chart-spinner
      p.text-center(v-if="testStatus && testStatus[0]") {{testStatus && testStatus[0]}}
      p.text-center(v-if="testStatus && testStatus[1]") {{testStatus && testStatus[1]}}
      button.btn.btn--dark-blue-rev.new-test(@click="stopTest()") Stop Test
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
      testTypeOptions: Object.keys(TestTypes)
        .filter(key => !TestTypes[key].disabled)
        .map(key => ({
          text: TestTypes[key].text,
          value: key
        })),
        TestTypes
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
    }
  }
};
</script>

<style lang="scss" scoped>
.test-header {
  padding: 12px 20px;
  border-bottom: 1px solid #b6c7fb;
}
.test-wrapper {
  background: linear-gradient(180deg, #363e51 0%, #000000 225%);
  display: flex;
  flex-direction: column;
}
.test-view {
  padding: 12px 20px;
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
  font-size: 14px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 1.2rem;
}
.run-test-button {
  font-size: 1.5rem;
  padding: 1.2em;
}
.form_label {
  margin-right: 1em;
}
.form_input {
  width: 150px;
}

.test-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  left: 0;
  z-index: 101;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background-color: rgba(35, 37, 42, 0.5);

  p {
    font-size: 16px;
  }
}
.spinner {
  position: relative;
  width: 20px;
  height: 0;
  overflow: visible;
  margin-bottom: 40px;
}
</style>
