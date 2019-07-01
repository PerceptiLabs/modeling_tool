<template lang="pug">
  .statistics-box
    ul.statistics-box_tabset(v-if="!testIsOpen")
      li.statistics-box_tab(
      v-for="(tab, i) in tabset"
      :key="i"
      )
        button.btn.btn--tabs.tutorial-relative(
        type="button"
        v-tooltip-interactive:right="tab.interactiveInfo"
        @click="setTab(tab.name, tab.id)"
        :class="{'active': currentTab === tab.name}"
        :id="tab.id"
        ) {{ tab.name }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row(v-if="!testIsOpen")
        .statistics-box_col
          chart-switch.data-charts(
            key="1"
            chart-label="Input"
            :chart-data="chartData.Prediction.Input"
            )
        .statistics-box_col
            chart-pie(
              key="8"
              chart-label="Accuracy"
              :chart-data="chartData.Prediction.Accuracy"
              :custom-color="colorPie"
            )
      .statistics-box_row
        .statistics-box_col
          chart-switch#tutorial_prediction-chart.data-charts(
            key="2"
            chart-label="Prediction vs Ground truth"
            :chart-data="chartData.Prediction.PvG"
            :custom-color="colorList"
            )
        .statistics-box_col(v-if="!testIsOpen")
          chart-switch.data-charts(
            key="3"
            chart-label="Batch Average Prediction vs Ground truth"
            :chart-data="chartData.Prediction.AveragePvG"
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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'F1'")
      chart-switch(
        chart-label="F1 during one epoch"
        :chart-data="chartData.F1.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        chart-label="F1 over all epochs"
        :chart-data="chartData.F1.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'AUC'")
      chart-switch(
        chart-label="AUC during one epoch"
        :chart-data="chartData.AUC.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        chart-label="AUC over all epochs"
        :chart-data="chartData.AUC.Total"
        :custom-color="colorListAccuracy"
      )
</template>

<script>
  import ChartSwitch      from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";
  import { mapActions } from 'vuex';

  export default {
    name: "ViewBoxTrainNormal",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: {
            Input: null,
            PvG: null,
            AveragePvG: null,
            Accuracy: null,
          },
          Accuracy: {
            Current: null,
            Total: null,
          },
          Loss: {
            Current: null,
            Total: null,
          },
          F1: {
            Current: null,
            Total: null,
          },
          AUC: {
            Current: null,
            Total: null,
          }
        },
        currentTab: 'Prediction',
        tabset: [
          {
            name: 'Prediction',
            id: 'tutorial_prediction-tab',
            interactiveInfo: {
              title: 'Prediction',
              text: 'View the input, current accuracy and <br/> output prediction vs ground truth/labels'
            }
          },
          {
            name: 'Accuracy',
            id: 'tutorial_accuracy-tab',
            interactiveInfo: {
              title: 'Accuracy',
              text: 'View the accuracy.'
            }
          },
          {
            name: 'Loss',
            id: 'tutorial_loss-tab',
            interactiveInfo: {
              title: 'Loss',
              text: 'View the loss.'
            }
          },
          {
            name: 'F1',
            id: 'tutorial_f1-tab',
            interactiveInfo: {
              title: 'F1',
              text: 'View the F1 score.'
            }
          },
          {
            name: 'AUC',
            id: 'tutorial_auc-tab',
            interactiveInfo: {
              title: 'AUC',
              text: 'View the AUC.'
            }
          },
        ],
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
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate',
      }),
      setTab(name, id) {
        this.currentTab = name;
        this.setTabAction();
        this.tutorialPointActivate({way: 'next', validation: id})
      },
      getData() {
        switch (this.currentTab) {
          case 'Prediction':
            this.chartRequest(this.statElementID, 'TrainNormal', 'Prediction');
            break;
          case 'Accuracy':
            this.chartRequest(this.statElementID, 'TrainNormal', 'Accuracy');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainNormal', 'Loss');
            break;
          case 'F1':
            this.chartRequest(this.statElementID, 'TrainNormal', 'F1');
            break;
          case 'AUC':
            this.chartRequest(this.statElementID, 'TrainNormal', 'AUC');
            break;
        }
      }
    },
  }
</script>
