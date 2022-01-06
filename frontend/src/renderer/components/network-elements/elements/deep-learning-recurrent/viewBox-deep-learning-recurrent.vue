<template lang="pug">
.statistics-box
  .statistics-box_main.statistics-box_col(
    v-if="currentTab === 'Output'"
  )
    chart-switch(
      key="1",
      chart-label="Output",
      :chart-data="chartData.Output.Output"
    )
</template>

<script>
import ChartSwitch from "@/components/charts/chart-switch.vue";
import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
export default {
  name: "ViewBoxDeepLearningRecurrent",
  components: { ChartSwitch },
  mixins: [viewBoxMixin],
  data() {
    return {
      chartData: {
        Output: {
          Output: null
        },
        WeightsBias: {
          Weights: null,
          Bias: null
        },
        Gradients: {
          Gradients: null
        }
      },
      //btnList: {'Output': null, 'Weights & Bias': null, 'Gradients': null},
      btnList: { Output: null },
      colorList: ["#83c1ff", "#0070d6", "#6b8ff7"]
    };
  },
  methods: {
    getData() {
      switch (this.currentTab) {
        case "Output":
          this.chartRequest(
            this.networkElement.layerId,
            "DeepLearningRecurrent",
            "Output"
          );
          break;
        case "Weights & Bias":
          this.chartRequest(
            this.networkElement.layerId,
            "DeepLearningRecurrent",
            "WeightsBias"
          );
          break;
        case "Gradients":
          this.chartRequest(
            this.networkElement.layerId,
            "DeepLearningRecurrent",
            "Gradients"
          );
          break;
      }
    }
  }
};
</script>
