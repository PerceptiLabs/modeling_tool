<template lang="pug">
  .statistics-box.statistics-box--horizontally
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output'")
      chart-switch(
        key="1"
        chart-label="Output"
        :chart-data="chartData.Output.Output"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Bias'")
      chart-switch(
        key="2"
        chart-label="Weights"
        :chart-data="chartData['Weights&Bias'].Weights"
      )
</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxPreTrainedMobileNetV2",
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
        },
        btnList: {'Output': null, 'Weights & Bias': null},
        colorList: ['#83c1ff', '#0070d6', '#6b8ff7']
      }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Output':
            this.chartRequest(this.boxElementID, 'PreTrainedMobileNetV2', 'Output');
            break;
          case 'Weights & Bias':
            this.chartRequest(this.boxElementID, 'PreTrainedMobileNetV2', 'Weights&Bias');
            break;
        }
      }
    }
  }
</script>
