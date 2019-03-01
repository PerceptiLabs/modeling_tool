<template lang="pug">
  .statistics-box
    ul.statistics-box_tabset(v-if="!testIsOpen")
      li.statistics-box_tab(
      v-for="(tab, i) in tabset"
      :key="i"
      )
        button.btn.btn--tabs(
        type="button"
        @click="setTab(tab)"
        :class="{'active': currentTab === tab}"
        :disabled="i > 2"
        ) {{ tab }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row(v-if="!testIsOpen")
        .statistics-box_col
          chart-base(
            chartLabel="Input"
            :chartData="chartData.Prediction.Input"
            )
      .statistics-box_row
        .statistics-box_col
          chart-base(
            chartLabel="Prediction vs Ground truth"
            :chartData="chartData.Prediction.PvG"
            :customColor="colorList"
          )
        .statistics-box_col(v-if="!testIsOpen")
          chart-base(
            chartLabel="Batch Average Prediction vs Ground truth"
            :chartData="chartData.Prediction.AveragePvG"
            :customColor="colorList"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="chartData.Accuracy.Current"
        :customColor="colorListAccuracy"
      )
      chart-base(
        chartLabel="Accuracy over all epochs"
        :chartData="chartData.Accuracy.Total"
        :customColor="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
        chartLabel="Loss during one epoch"
        :chartData="chartData.Loss.Current"
        :customColor="colorListAccuracy"
      )
      chart-base(
        chartLabel="Loss over all epochs"
        :chartData="chartData.Loss.Total"
        :customColor="colorListAccuracy"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'F1'")
      chart-base(
      chartLabel="F1 during one epoch"
      /:chartData="optionLine1"
      )
      chart-base(
      chartLabel="F1 over all epochs"
      /:chartData="optionLine1"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'Precision & Recall'")
      chart-base(
      /:chartData="optionLine1"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'ROC'")
      chart-base(
      /:chartData="optionLine1"
      )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";

  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxTrainNormal",
    components: {ChartBase, ChartHeatmap, ChartD3},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: {
            Input: null,
            PvG: null,
            AveragePvG: null,
          },
          Accuracy: {
            Current: null,
            Total: null,
          },
          Loss: {
            Current: null,
            Total: null,
          }
        },
        currentTab: 'Prediction',
        tabset: ['Prediction', 'Accuracy', 'Loss', 'F1', 'Precision & Recall', 'ROC'],
        colorList: ['#6B8FF7', '#FECF73'],
        colorListAccuracy: ['#9173FF', '#6B8FF7'],

      }
    },
    methods: {
      setTab(name) {
        this.currentTab = name;
        this.setTabAction();
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
        }
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
