<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row(v-if="!testIsOpen")
        .statistics-box_col
          chart-switch(
            key="1"
            chart-label="Input"
            :chart-data="chartData.Prediction.Input"
            )
        .statistics-box_col
          chart-switch(
            key="8"
            chart-label="Accuracy"
            :chart-data="chartData.Prediction.Accuracy"
            :custom-color="colorPie"
            )
      .statistics-box_row
        .statistics-box_col
          chart-switch#tutorial_prediction-chart(
            key="2"
            chart-label="Prediction vs Ground truth"
            :chart-data="chartData.Prediction.PvG"
            :custom-color="colorList"
            )
        .statistics-box_col(v-if="!testIsOpen")
          chart-switch(
            key="3"
            chart-label="Batch Average Prediction vs Ground truth"
            :chart-data="chartData.Prediction.AveragePvG"
            :custom-color="colorList"
            )
</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";
  import { mapActions } from 'vuex';

  export default {
    name: "ViewBoxIoOutput",
    components: { ChartSwitch },
    mixins: [ viewBoxMixin ],
    data() {
      return {
        chartData: {
          Prediction: { Input: null, PvG: null, AveragePvG: null, Accuracy: null },
        },
        btnList: {
          'Prediction': {
            btnId: 'tutorial_prediction-tab',
            btnInteractiveInfo: {
              title: 'Prediction',
              text: 'View the input, current accuracy and <br/> output prediction vs ground truth/labels'
            }
          },
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
          case 'Prediction':
            this.chartRequest(this.statElementID, 'IoOutput', 'Prediction');
            break;
        }
      }
    }
  }
</script>
