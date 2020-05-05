
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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-switch(
        key="6"
        chart-label="Loss during one epoch"
        :chart-data="chartData.Loss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="7"
        chart-label="Loss over all epochs"
        :chart-data="chartData.Loss.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'R_Squared'")
      chart-switch(
        key="11"
        chart-label="R Squared data during one epoch"
        :chart-data="chartData.R_Squared.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="12"
        chart-label="R Squared data over all epochs"
        :chart-data="chartData.R_Squared.Total"
        :custom-color="colorListAccuracy"
      )
</template>

<script>
  import ChartSwitch      from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";


  export default {
    name: "ViewBoxTrainRegression",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: { Input: null, PvG: null, AveragePvG: null, Accuracy: null, R_Squared: null, AveragePvT: null },
          Loss:       { Current: null, Total: null },
          R_Squared:        { Current: null, Total: null }
        },
        btnList: {
          'Prediction': {
            btnId: 'tutorial_prediction-tab',
            btnInteractiveInfo: {
              title: 'Prediction',
              text: 'View prediction data'
            }
          },
          'Loss': {
            btnId: 'tutorial_loss-tab',
            btnInteractiveInfo: {
              title: 'Loss',
              text: 'View the loss.'
            }
          },
          'R_Squared': {
            btnId: 'tutorial_r_squared-tab',
            btnInteractiveInfo: {
              title: 'R Squared',
              text: 'View the R Squared data.'
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
      // testIsOpen(newVal) {
      //   newVal ? this.setTab('Prediction') : null
      // }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Prediction':
            this.chartRequest(this.statElementID, 'TrainRegression', 'Prediction');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainRegression', 'Loss');
            break;
          case 'R_Squared':
            this.chartRequest(this.statElementID, 'TrainRegression', 'R_Squared');
            break;
        }
      }
    },
  }
</script>
