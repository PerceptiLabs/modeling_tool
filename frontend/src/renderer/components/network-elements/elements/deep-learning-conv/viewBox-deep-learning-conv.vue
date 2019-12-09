<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Output'")
      .statistics-box_row
        .statistics-box_col(v-if="!testIsOpen")
          chart-switch(
            key="1"
            chart-label="Weights"
            :chart-data="chartData['Weights&Output'].Weights"
            )
        .statistics-box_col
          chart-switch(
            key="2"
            chart-label="Output"
            :chart-data="chartData['Weights&Output'].Output"
            )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Bias'")
      .statistics-box_row
        chart-switch(
          key="3"
          chart-label="Bias"
          :chart-data="chartData.Bias.Bias"
        )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Gradients'")
      chart-switch(
        key="4"
        chart-label="Bias"
        :chart-data="chartData.Gradients.Gradients"
        :custom-color="colorList"
      )
</template>

<script>
  import ChartSwitch      from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxDeepLearningConv",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          'Weights&Output': {
            Weights: null,
            Output: null,
          },
          Bias: {
            Bias: null,
          },
          Gradients: {
            Gradients: null,
          }},
        btnList: {'Weights & Output': null, 'Bias': null, 'Gradients': null},
        colorList: ['#83c1ff', '#0070d6', '#6b8ff7']
      }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Weights & Output':
            this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Weights&Output');
            break;
          case 'Bias':
            this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Bias');
            break;
          case 'Gradients':
            this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Gradients');
            break;
        }
      }
    },
  }
</script>
