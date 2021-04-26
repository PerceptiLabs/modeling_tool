<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab !== 'Global'")
      template(v-if="sectionTitle === 'Statistics'")
        .statistics-box_main.statistics-box_col(v-if="chartData.hasOwnProperty('Accuracy')")
          .statistics-box_row
            chart-switch(
              key="4"
              chart-label="Accuracy during one epoch"
              :chart-data="chartData.Accuracy.OverSteps"
              :custom-color="colorListAccuracy"
            )
            chart-switch(
              key="5"
              chart-label="Accuracy over all epochs"
              :chart-data="chartData.Accuracy.OverEpochs"
              :custom-color="colorListAccuracy"
            )
        .statistics-box_main.statistics-box_col(v-if="chartData.hasOwnProperty('PvG')")
          .statistics-box_row
            chart-switch(
              key="6"
              chart-label="Prediction vs Ground truth"
              :chart-data="chartData.PvG.Sample"
              :custom-color="colorList"
            )
            chart-switch(
              key="7"
              chart-label="Batch Average Prediction vs Ground truth"
              :chart-data="chartData.PvG.BatchAverage"
              :custom-color="colorList"
            )
        .statistics-box_main.statistics-box_col(v-if="chartData.hasOwnProperty('IoU')")
          .statistics-box_row
            chart-switch(
              key="4"
              chart-label="IoU during one epoch"
              :chart-data="chartData.IoU.OverSteps"
              :custom-color="colorListAccuracy"
            )
            chart-switch(
              key="5"
              chart-label="IoU over all epochs"
              :chart-data="chartData.IoU.OverEpochs"
              :custom-color="colorListAccuracy"
            ) 
      template(v-else)
        .statistics-box_main.statistics-box_col(v-if="chartData.hasOwnProperty('ViewBox')")
          .statistics-box_row
            chart-switch(
              key="4"
              chart-label="Output"
              :chart-data="chartData.ViewBox.Output"
              :custom-color="colorListAccuracy"
            )
        
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Global' && chartData.Loss")
      template(v-if="sectionTitle === 'Statistics'")
        chart-switch(
          key="6"
          chart-label="Loss during one epoch"
          :chart-data="chartData.Loss.OverEpochs"
          :custom-color="colorListAccuracy"
        )
        chart-switch(
          key="7"
          v-if="chartData.Loss.OverSteps"
          chart-label="Loss over all epochs"
          :chart-data="chartData.Loss.OverSteps"
          :custom-color="colorListAccuracy"
        )
      tempalate(v-else)
        chart-switch(
          key="4"
          chart-label="Output"
          :chart-data="chartData.ViewBox.Output"
          :custom-color="colorListAccuracy"
      )
</template>

<script>
import ChartSwitch from "@/components/charts/chart-switch";
import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
import netIOTabs from "@/core/mixins/net-IO-tabs.js";
import {mapActions} from 'vuex';
import {coreRequest} from "@/core/apiWeb";
import Vue from "vue";

export default {
  name: "ViewBoxIoOutput",
  components: {ChartSwitch},
  mixins: [viewBoxMixin, netIOTabs],
  props: {
    el: Object,
  },
  data() {
    return {
      chartData: {
        Data: {},
        Loss: {},
        Accuracy: {
          OverEpochs: {},
          OverSteps: {},
        },
        PvG: {
          Sample: {},
          BatchAverage: {},
        },
        ViewBox: {
          Output: {},
        }
      },

      colorList: ['#6B8FF7', '#FECF73'],
      colorListAccuracy: ['#9173FF', '#6B8FF7'],
      colorPie: ['#6B8FF7', '#383F50'],
      showRequestSpinner: {
        Input: true,
        PvG: true,
        AveragePvG: true,
        Accuracy: true
      }
    }
  },
  watch: {
    testIsOpen(newVal) {
      newVal ? this.setTab('Prediction') : null
    }
  },
  methods: {
    getData() {
      switch (this.currentTab) {
        case 'Global':
          this.chartGlobalRequest();
          break;
        default:
          this.chartRequest(this.statElementID, 'IoOutput', '');
          break;
      }
    },
  }
}
</script>
