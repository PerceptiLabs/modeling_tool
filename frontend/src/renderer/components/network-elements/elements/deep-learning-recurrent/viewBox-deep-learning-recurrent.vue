<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output' && isWeb")
      chart-switch(
        key="1"
        chart-label="Output"
        :chart-data="chartData.Output.Output"
        )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output' && chartData.Output && isElectron")
      chart-switch(
        key="1"
        chart-label="Value"
        :chart-data="chartData.Output.Output"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Bias' && chartData['Weights&Bias'] && isElectron")
      chart-switch(
        key="2"
        chart-label="Weights"
        :chart-data="chartData['Weights&Bias'].Weights"
      )
      chart-switch(
        key="3"
        chart-label="Bias"
        :chart-data="chartData['Weights&Bias'].Bias"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Gradients' && chartData.Gradients && isElectron")
      chart-switch(
        key="4"
        chart-label="Bias"
        :chart-data="chartData.Gradients.Gradients"
        :custom-color="colorList"
      )
</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  import {isElectron, isWeb} from "@/core/helpers";
  export default {
    name: "ViewBoxDeepLearningRecurrent",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        isWeb: isWeb(),
        isElectron: isElectron(),
        chartData: {
          Output: {
            Output: null,
          },
          'Weights&Bias': {
            Weights: null,
            Bias: null,
          },
          Gradients: {
            Gradients: null,
          }
        },
        //btnList: {'Output': null, 'Weights & Bias': null, 'Gradients': null},
        btnList: {'Output': null},
        colorList: ['#83c1ff', '#0070d6', '#6b8ff7']
      }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Output':
            this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Output');
            break;
          case 'Weights & Bias':
            this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Weights&Bias');
            break;
          case 'Gradients':
            this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Gradients');
            break;
        }
      }
    }
  }
</script>
