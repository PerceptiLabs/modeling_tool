<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab !== 'Global'")
      chart-switch(
        key="1"
        chart-label="Data"
        :chart-data="chartData.Data"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Global' && chartData.Loss")
      chart-switch(
        key="2"
        chart-label="Loss during one epoch"
        :chart-data="chartData.Loss.OverSteps"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="3"
        chart-label="Loss over all epochs"
        :chart-data="chartData.Loss.OverEpochs"
        :custom-color="colorListAccuracy"
      )
</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  import netIOTabs    from "@/core/mixins/net-IO-tabs.js";
  export default {
    name: "ViewBoxIoInput",
    components: {ChartSwitch},
    mixins: [viewBoxMixin, netIOTabs],
    data() {
      return {
        chartData: {
          Data: {},
          Loss: {
            OverEpochs: {},
            OverSteps: {},
          }
        },
        colorListAccuracy: ['#9173FF', '#6B8FF7'],
      }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Global':
            this.chartGlobalRequest();
            break;
          default:
            this.chartRequest(this.networkElement.layerId, 'IoInput', '');
            break;
        }
      },
    }
  }
</script>
