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
          key="2"
          chartLabel="Prediction vs Ground truth"
          :chartData="chartData.Prediction.PvG"
          :customColor="colorList"
          )
        .statistics-box_col
          chart-base(
          key="3"
          chartLabel="Batch Average Prediction vs Ground truth"
          :chartData="chartData.Prediction.AveragePvG"
          :customColor="colorList"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Reward'")
      chart-base(
      key="4"
      chartLabel="Accuracy during one epoch"
      :chartData="chartData.Reward.Current"
      )
      chart-base(
      key="5"
      chartLabel="Accuracy over all epochs"
      :chartData="chartData.Reward.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
      key="6"
      chartLabel="Loss during one epoch"
      :chartData="chartData.Loss.Current"
      )
      chart-base(
      key="7"
      chartLabel="Loss over all epochs"
      :chartData="chartData.Loss.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Steps'")
      chart-base(
      key="8"
      chartLabel="Loss over all epochs"
      :chartData="chartData.Steps.Total"
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
        tabset: ['Prediction', 'Reward', 'Loss', 'Steps'],
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
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Prediction');
            break;
          case 'Accuracy':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Reward');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Loss');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Steps');
            break;
        }
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
