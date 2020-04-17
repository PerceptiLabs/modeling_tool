<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row(v-if="!testIsOpen")
        .statistics-box_col
          chart-switch(
            key="1"
            chart-label="Bboxes"
            :chart-data="chartData.Prediction.Bboxes"
            )
        .statistics-box_col
          .statistics-box_row
            chart-switch#tutorial_prediction-chart(
              key="2"
              chart-label="Accuracy"
              :chart-data="chartData.Prediction.Accuracy"
              :custom-color="colorPie"
              )
          .statistics-box_row(v-if="!testIsOpen")
            chart-switch(
              key="3"
              chart-label="Confidence"
              :chart-data="chartData.Prediction.Confidence"
              :custom-color="colorList"
              )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-switch(
        key="4"
        chart-label="Accuracy during one epoch"
        :chart-data="chartData.Accuracy.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="5"
        chart-label="Accuracy over all epochs"
        :chart-data="chartData.Accuracy.Total"
        :custom-color="colorListAccuracy"
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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Classification Loss'")
      chart-switch(
        key="9"
        chart-label="Classification Loss during one epoch"
        :chart-data="chartData.ClassificationLoss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="10"
        chart-label="Classification Loss over all epochs"
        :chart-data="chartData.ClassificationLoss.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Bounding Boxes Loss'")
      chart-switch(
        key="11"
        chart-label="Bounding Boxes Loss during one epoch"
        :chart-data="chartData.BoundingBoxesLoss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="12"
        chart-label="Bounding Boxes Loss over all epochs"
        :chart-data="chartData.BoundingBoxesLoss.Total"
        :custom-color="colorListAccuracy"
      )
</template>

<script>
  import ChartSwitch      from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";


  export default {
    name: "ViewBoxTrainDetector",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: { Bboxes: null, Confidence: null, Accuracy: null },
          Accuracy:   { Current: null, Total: null },
          Loss:       { Current: null, Total: null },
          ClassificationLoss:         { Current: null, Total: null },
          BoundingBoxesLoss:        { Current: null, Total: null }
        },
        btnList: {
          'Prediction': {
            btnId: 'tutorial_prediction-tab',
            btnInteractiveInfo: {
              title: 'Prediction',
              text: 'View the input, current accuracy and <br/> output prediction vs ground truth/labels'
            }
          },
          'Accuracy': {
            btnId: 'tutorial_accuracy-tab',
            btnInteractiveInfo: {
              title: 'Accuracy',
              text: 'View the accuracy.'
            }
          },
          'Loss': {
            btnId: 'tutorial_loss-tab',
            btnInteractiveInfo: {
              title: 'Loss',
              text: 'View the loss.'
            }
          },
          'Classification Loss': {
            btnId: 'tutorial_classification_loss-tab',
            btnInteractiveInfo: {
              title: 'Classification Loss',
              text: 'View the Classification Loss'
            }
          },
          'Bounding Boxes Loss': {
            btnId: 'tutorial_bounding_boxes_loss-tab',
            btnInteractiveInfo: {
              title: 'Bounding Boxes Loss',
              text: 'View the Bounding Boxes Loss'
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
            this.chartRequest(this.statElementID, 'TrainDetector', 'Prediction');
            break;
          case 'Accuracy':
            this.chartRequest(this.statElementID, 'TrainDetector', 'Accuracy');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainDetector', 'Loss');
            break;
          case 'Classification Loss':
            this.chartRequest(this.statElementID, 'TrainDetector', 'ClassificationLoss');
            break;
          case 'Bounding Boxes Loss':
            this.chartRequest(this.statElementID, 'TrainDetector', 'BoundingBoxesLoss');
            break;
        }
      }
    },
  }
</script>
