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
        ) {{ tab }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row
        .statistics-box_col(v-if="!testIsOpen")
          chart-picture(
            key="2"
            chart-label=""
            :chart-data="chartData.Prediction.Input"
          )
        .statistics-box_col
          chart-base(
            key="3"
            chart-label=""
            :chart-data="chartData.Prediction.Prediction"
            :custom-color="colorList"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Reward'")
      chart-base(
        key="4"
        chart-label=""
        :chart-data="chartData.Reward.Current"
      )
      chart-base(
        key="5"
        chart-label=""
        :chart-data="chartData.Reward.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
        key="6"
        chart-label=""
        :chart-data="chartData.Loss.Current"
      )
      chart-base(
        key="7"
        chart-label=""
        :chart-data="chartData.Loss.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Steps'")
      chart-base(
        key="8"
        chart-label=""
        :chart-data="chartData.Steps.Steps"
      )

</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";
  import ChartPicture    from "@/components/charts/chart-picture.vue";

  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxTrainReinforce",
    components: {ChartBase, ChartHeatmap, ChartD3, ChartPicture},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: {
            Input: null,
            PvG: null,
            AveragePvG: null,
          },
          Reward: {
            Current: null,
            Total: null,
          },
          Loss: {
            Current: null,
            Total: null,
          },
          Steps: {
            Steps: null
          }
        },
        currentTab: 'Prediction',
        tabset: ['Prediction', 'Reward', 'Loss', 'Steps'],
        colorList: ['#6B8FF7', '#FECF73'],
      }
    },
    watch: {
      testIsOpen(newVal) {
        newVal ? this.setTab('Prediction') : null
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
          case 'Reward':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Reward');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Loss');
            break;
          case 'Steps':
            this.chartRequest(this.statElementID, 'TrainReinforce', 'Steps');
            break;
        }
      }
    },
  }
</script>
