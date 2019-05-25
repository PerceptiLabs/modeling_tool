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
        ) {{ tab }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row
        .statistics-box_col
          chart-base(
            :chart-data="optionLine1"
          )
          chart-base(
            chart-label="Accuracy over all epochs"
            :chart-data="optionLine1"
          )
          chart-base(
            :chart-data="optionLine1"
          )
        .statistics-box_col
          chart-heatmap(
            :chart-data="optionHeat"
          )
        .statistics-box_col
          chart-d3(
            :chart-data="option3d"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-base(
        chart-label="Accuracy during one epoch"
        :chart-data="optionLine1"
      )
      chart-base(
        chart-label="Accuracy over all epochs"
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
        chart-label="Loss during one epoch"
        :chart-data="optionLine1"
      )
      chart-base(
        chart-label="Loss over all epochs"
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'F1'")
      chart-base(
        chart-label="F1 during one epoch"
        :chart-data="optionLine1"
      )
      chart-base(
        chart-label="F1 over all epochs"
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Precision & Recall'")
      chart-base(
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'ROC'")
      chart-base(
        :chart-data="optionLine1"
      )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";
  import data3d       from "@/components/charts/3d.js";

  export default {
    name: "ViewBoxTrainDynamic",
    components: {ChartBase, ChartHeatmap, ChartD3},
    data() {
      return {
        currentTab: 'Prediction',
        tabset: ['Prediction', 'Accuracy', 'Loss', 'F1', 'Precision & Recall', 'ROC'],
        optionLine1: null,
        option3d: data3d,
        optionHeat: null,
        optionBar: null,
      }
    },
    methods: {
      setTab(name) {
        this.currentTab = name
      }
    }
  }
</script>
