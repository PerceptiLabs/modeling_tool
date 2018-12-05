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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction' && chartData.Prediction")
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
          )
        .statistics-box_col
          chart-base(
          chartLabel="Batch Average Prediction vs Ground truth"
          :chartData="chartData.Prediction.AveragePvG"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy' && chartData.Accuracy")
      chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="chartData.Accuracy.Current"
      )
      chart-base(
        chartLabel="Accuracy over all epochs"
        :chartData="chartData.Accuracy.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss' && chartData.Loss")
      chart-base(
        chartLabel="Loss during one epoch"
        :chartData="chartData.Loss.Current"
      )
      chart-base(
        chartLabel="Loss over all epochs"
        :chartData="chartData.Loss.Total"
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
  import data3d       from "@/components/charts/3d.js";
  import dataHeat     from "@/components/charts/hear.js";
  import dataBar      from "@/components/charts/bar.js";
  import dataLine     from "@/components/charts/line.js";

  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxTrainNormal",
    components: {ChartBase, ChartHeatmap, ChartD3},
    mixins: [viewBoxMixin],
    data() {
      return {
        currentTab: 'Prediction',
        tabset: ['Prediction', 'Accuracy', 'Loss', 'F1', 'Precision & Recall', 'ROC'],
      }
    },
    methods: {
      setTab(name) {
        clearInterval(this.idTimer);
        this.currentTab = name;
        if(name === 'Prediction') {
          this.getStatistics()
        }
        else if (name === 'Accuracy') {
          this.getAccStatistics()
        }
        else if (name === 'Loss') {
          this.getLossStatistics()
        }
      },
      getStatistics() {
        this.chartRequest(this.statElementID, 'TrainNormal', 'Prediction')
      },
      getAccStatistics() {
        this.chartRequest(this.statElementID, 'TrainNormal', 'Accuracy')
      },
      getLossStatistics() {
        this.chartRequest(this.statElementID, 'TrainNormal', 'Loss')
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
