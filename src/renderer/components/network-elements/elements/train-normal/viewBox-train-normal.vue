<template lang="pug">
  .statistics-box
    ul.statistics-box_tabset(v-if="!testIsOpen")
      li.statistics-box_tab(
      v-for="(tab, i) in tabset"
      :key="i"
      )
        button.btn.btn--tabs.tutorial-relative(
        type="button"
        @click="setTab(tab.name, tab.id)"
        :class="{'active': currentTab === tab.name}"
        :disabled="i > 2"
        :id="tab.id"
        ) {{ tab.name }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row(v-if="!testIsOpen")
        .statistics-box_col
          chart-switch(
            key="1"
            chartLabel="Input"
            :chartData="chartData.Prediction.Input"
            )
        .statistics-box_col
          chart-pie(
            key="8"
            chartLabel="Accuracy"
            :chartData="chartData.Prediction.Accuracy"
            :customColor="colorPie"
          )
      .statistics-box_row
        .statistics-box_col
          chart-base#tutorial_prediction-chart(
            key="2"
            chartLabel="Prediction vs Ground truth"
            :chartData="chartData.Prediction.PvG"
            :customColor="colorList"
          )
        .statistics-box_col(v-if="!testIsOpen")
          chart-base(
            key="3"
            chartLabel="Batch Average Prediction vs Ground truth"
            :chartData="chartData.Prediction.AveragePvG"
            :customColor="colorList"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-base(
        key="4"
        chartLabel="Accuracy during one epoch"
        :chartData="chartData.Accuracy.Current"
        :customColor="colorListAccuracy"
      )
      chart-base(
        key="5"
        chartLabel="Accuracy over all epochs"
        :chartData="chartData.Accuracy.Total"
        :customColor="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
        key="6"
        chartLabel="Loss during one epoch"
        :chartData="chartData.Loss.Current"
        :customColor="colorListAccuracy"
      )
      chart-base(
        key="7"
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
  import ChartPie    from "@/components/charts/chart-pie";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";
  import ChartSwitch      from "@/components/charts/chart-switch.vue";

  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  import { mapActions } from 'vuex';

  export default {
    name: "ViewBoxTrainNormal",
    components: {ChartBase, ChartPie, ChartHeatmap, ChartD3, ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: {
            Input: null,
            PvG: null,
            AveragePvG: null,
            Accuracy: null
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
        tabset: [
          {name: 'Prediction',        id: 'tutorial_prediction-tab'}, 
          {name: 'Accuracy',          id: 'tutorial_accuracy-tab'},
          {name: 'Loss',              id: 'tutorial_loss-tab'}, 
          {name: 'F1',                id: 'tutorial_f1-tab'}, 
          {name: 'Precision & Recall',id: 'tutorial_precision-tab'}, 
          {name: 'ROC',               id: 'tutorial_roc-tab'}
        ],
        colorList: ['#6B8FF7', '#FECF73'],
        colorListAccuracy: ['#9173FF', '#6B8FF7'],
        colorPie: ['#6B8FF7', '#383F50']
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
        }
      }
    },
  }
</script>

<style lang="scss" scoped>

</style>
