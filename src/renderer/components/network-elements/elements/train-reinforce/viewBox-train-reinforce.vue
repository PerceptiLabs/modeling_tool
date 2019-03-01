<template lang="pug">
  .statistics-box
    ul.statistics-box_tabset
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
      .statistics-box_row
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
        .statistics-box_col
          chart-base(
          chartLabel="Batch Average Prediction vs Ground truth"
          :chartData="chartData.Prediction.AveragePvG"
          :customColor="colorList"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-base(
      chartLabel="Accuracy during one epoch"
      :chartData="chartData.Accuracy.Current"
      )
      chart-base(
      chartLabel="Accuracy over all epochs"
      :chartData="chartData.Accuracy.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
      chartLabel="Loss during one epoch"
      :chartData="chartData.Loss.Current"
      )
      chart-base(
      chartLabel="Loss over all epochs"
      :chartData="chartData.Loss.Total"
      )
  //-.statistics-box
    ul.statistics-box_tabset
      li.statistics-box_tab(
      v-for="(tab, i) in tabset"
      /:key="i"
      )
        button.btn.btn--tabs(
        type="button"
        @click="setTab(tab)"
        /:class="{'active': currentTab === tab}"
        ) {{ tab }}
    //-.statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row
        .statistics-box_col
          chart-base(
          /:chartData="optionBar"
          )
        .statistics-box_col
          chart-base(
          chartLabel="Reward during one epoch"
          /:chartData="optionLine1"
          )
    //-.statistics-box_main.statistics-box_col(v-if="currentTab === 'Reward'")
      chart-base(
      chartLabel="Reward during one epoch"
      /:chartData="optionLine1"
      )
      chart-base(
      chartLabel="Reward over all"
      /:chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
      chartLabel="Loss during one epoch"
      /:chartData="optionLine1"
      )
      chart-base(
      chartLabel="Loss over all"
      /:chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Steps'")
      chart-base(
      chartLabel="Steps per epoch"
      /:chartData="optionLine1"
      )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";

  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxTrainReinforce",
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
          }},
        currentTab: 'Prediction',
        tabset: ['Prediction', 'Accuracy', 'Loss', 'F1', 'Precision & Recall', 'ROC'],
        colorList: ['#ff0', '#0f0']
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
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Prediction')
            break;
          case 'Accuracy':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Accuracy');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Loss');
            break;
        }
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
