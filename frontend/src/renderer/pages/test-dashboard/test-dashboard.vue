<template lang="pug">
  div.wrapper
    .chart-wrapper
      template(v-for="(testTypes, key) in testData")
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
                :chart-label="`${modelName(chartId) } - ${featureName} ${testTypesPretty[key]}`"
                :chart-data="feature"
                :styles="chartStyles"
              )
</template>
<script>
import ChartSwitch    from "@/components/charts/chart-switch";
import MetricTestTable  from "./components/metric-test-table";
import { mapGetters } from 'vuex';
import { getFirstElementFromObject } from "@/core/helpers";

const chartStyles = {
  main: {
    'min-height': 'calc(50vh - 150px)'
  }
}

export default {
  name: "TestDashboard",
  components: {ChartSwitch, MetricTestTable },
  created() {
    this.$store.dispatch('mod_webstorage/getTestStatistic')
      .then(res => {
        this.$store.dispatch('mod_test/setTestData', res, {root: true});
      })
  },
  data() {
    return {
      chartStyles,
      testTypesPretty: {
        'confusion_matrix': 'Confusion matrix',
      },
    }
  },
  computed: {
    ...mapGetters({
      testData: 'mod_test/GET_testData',
    }),
  },
  methods: {
    modelName(id){
      return this.$store.getters['mod_workspace/GET_modelName'](id);
    },
    getMetricTableFeatures(data) {
      const chartData = getFirstElementFromObject(data);
      return Object.keys(chartData);
    }
  }
}
</script>
<style lang="scss" scoped>
  .wrapper {
    position: relative;
    margin-top: 4px;
    height: 100%;
    background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border: 1px solid rgba(97, 133, 238, 0.4);
    padding-left: 10px;
    padding-right: 19px;
  }
  .chart-wrapper {
    display: flex;
    align-content: start;
    flex-wrap: wrap;
  }
  .chart-container {
    width: calc(50% - 40px);
    margin: 20px;
  }
</style>