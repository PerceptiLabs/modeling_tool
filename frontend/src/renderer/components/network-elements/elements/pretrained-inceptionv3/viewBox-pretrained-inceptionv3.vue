<template lang="pug">
.statistics-box.statistics-box--horizontally
  .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output'")
    chart-switch(
      key="1",
      chart-label="Output",
      :chart-data="chartData.Output.Output"
    )
  .statistics-box_main.statistics-box_col(
    v-if="currentTab === 'Weights & Bias'"
  )
    chart-switch(
      key="2",
      chart-label="Weights & Bias",
      :chart-data="chartData['WeightsBias'].Weights"
    )
</template>

<script>
import ChartSwitch from "@/components/charts/chart-switch.vue";
import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
export default {
  name: "ViewBoxPreTrainedInceptionV3",
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
        }
      },
      btnList: { Output: null, "Weights & Bias": null },
      colorList: ["#83c1ff", "#0070d6", "#6b8ff7"]
    };
  },
  methods: {
    getData() {
      switch (this.currentTab) {
        case "Output":
          this.chartRequest(
            this.networkElement.layerId,
            "PreTrainedInceptionV3",
            "Output"
          );
          break;
        case "Weights & Bias":
          this.chartRequest(
            this.networkElement.layerId,
            "PreTrainedInceptionV3",
            "WeightsBias"
          );
          break;
      }
    }
  }
};
</script>
