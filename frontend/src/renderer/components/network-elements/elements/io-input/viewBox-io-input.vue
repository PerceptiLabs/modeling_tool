<template lang="pug">
.statistics-box
  .statistics-box_toolbar.text-center.mb-10(
    v-if="currentTab === 'Input' && sectionTitle==='Statistics' && inputs && inputs.length > 1"
  )
    base-select.input-select(
      :select-options="inputOptions",
      :value="selectedInput",
      @input="setSelectInput($event)"
    )
  .statistics-box_main.statistics-box_col.overflow-hidden(v-if="currentTab !== 'Global Loss'")
    chart-switch(key="1", chart-label="Data", :chart-data="chartData.Data")
  .statistics-box_main.statistics-box_col(
    v-if="currentTab === 'Global Loss' && chartData.Loss"
  )
    chart-switch(
      key="2",
      chart-label="Loss during one epoch",
      :chart-data="chartData.Loss.OverSteps",
      :custom-color="colorListAccuracy"
    )
    chart-switch(
      key="3",
      chart-label="Loss over all epochs",
      :chart-data="chartData.Loss.OverEpochs",
      :custom-color="colorListAccuracy"
    )
</template>

<script>
import { mapGetters } from "vuex";
import ChartSwitch from "@/components/charts/chart-switch.vue";
import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
import netIOTabs from "@/core/mixins/net-IO-tabs.js";
import { deepCloneNetwork } from "@/core/helpers.js";

export default {
  name: "ViewBoxIoInput",
  components: { ChartSwitch },
  mixins: [viewBoxMixin, netIOTabs],
  data() {
    return {
      chartData: {
        Data: {},
        Loss: {
          OverEpochs: {},
          OverSteps: {}
        }
      },
      colorListAccuracy: ["#9173FF", "#6B8FF7"],
      selectedInput: this.networkElement.layerId,
    };
  },
  computed: {
    ...mapGetters({
      inputs: "mod_workspace/GET_inputs",
    }),
    inputOptions() {
      return this.inputs
        ? this.inputs.map((input) => {
            return {
              text: input.layerName,
              value: input.layerId,
            };
          })
        : [];
    },
  },
  methods: {
    getData() {
      switch (this.currentTab) {
        case "Global Loss":
          this.chartGlobalRequest();
          break;
        default:
          this.chartRequest(this.networkElement.layerId, "IoInput", "");
          break;
      }
    },
    setSelectInput(ev) {
      this.selectedInput = ev;

      let element = this.$store.getters[
        "mod_workspace/GET_networkSnapshotElementById"
      ](this.selectedInput);

      this.$store.commit(
        "mod_statistics/CHANGE_StatisticSelectedArr",
        deepCloneNetwork(element),
      );
    },
  }
};
</script>

<style lang="scss" scoped>
.mb-10 {
  margin-bottom: 10px;
}

.input-select {
  max-width: 300px;
  display: inline-block;
}

.overflow-hidden {
  overflow: hidden;
}
</style>