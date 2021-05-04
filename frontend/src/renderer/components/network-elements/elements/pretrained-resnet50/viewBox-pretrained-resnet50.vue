<template lang="pug">
  .statistics-box.statistics-box--horizontally
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output'")
      chart-switch(
        key="1"
        chart-label="Value"
        :chart-data="chartData.Output.Output"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Bias'")
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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Gradients'")
      chart-switch(
        key="4"
        chart-label="Gradients"
        :chart-data="chartData.Gradients.Gradients"
        :custom-color="colorList"
      )
</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxPreTrainedResNet50",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
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
        btnList: {'Output': null, 'Weights & Bias': null, 'Gradients': null},
        colorList: ['#83c1ff', '#0070d6', '#6b8ff7']
      }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Output':
            this.chartRequest(this.networkElement.layerId, 'PreTrainedResNet50', 'Output');
            break;
          case 'Weights & Bias':
            this.chartRequest(this.networkElement.layerId, 'PreTrainedResNet50', 'Weights&Bias');
            break;
          case 'Gradients':
            this.chartRequest(this.networkElement.layerId, 'PreTrainedResNet50', 'Gradients');
            break;
        }
      }
    }
  }
</script>
