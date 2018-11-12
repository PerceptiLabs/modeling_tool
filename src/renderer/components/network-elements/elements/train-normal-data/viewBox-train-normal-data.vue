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
          chart-bar(
          :chartData="optionLine1"
          )
          chart-bar(
          chartLabel="Accuracy over all epochs"
          :chartData="optionLine1"
          )
          chart-bar(
          :chartData="optionLine1"
          )
        .statistics-box_col
          chart-heatmap(
          :chartData="optionHeat"
          )
        .statistics-box_col
          chart-d3(
          :chartData="option3d"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine1"
      )
      chart-line(
      chartLabel="Accuracy over all epochs"
      :chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-line(
      chartLabel="Loss during one epoch"
      :chartData="optionLine1"
      )
      chart-line(
      chartLabel="Loss over all epochs"
      :chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'F1'")
      chart-line(
      chartLabel="F1 during one epoch"
      :chartData="optionLine1"
      )
      chart-line(
      chartLabel="F1 over all epochs"
      :chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Precision & Recall'")
      chart-line(
      :chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'ROC'")
      chart-line(
      :chartData="optionLine1"
      )
</template>

<script>
  import ChartLine    from "@/components/charts/chart-line";
  import ChartBar     from "@/components/charts/chart-bar.vue";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";
  import data3d       from "@/components/charts/3d.js";
  import dataHeat     from "@/components/charts/hear.js";
  import dataBar      from "@/components/charts/bar.js";
  import dataLine     from "@/components/charts/line.js";

  export default {
    name: "ViewBoxTrainNormalData",
    components: {ChartLine, ChartBar, ChartHeatmap, ChartD3},
    data() {
      return {
        currentTab: 'Prediction',
        tabset: ['Prediction', 'Accuracy', 'Loss', 'F1', 'Precision & Recall', 'ROC'],
        optionLine1: dataLine,
        option3d: data3d,
        optionHeat: dataHeat,
        optionBar: dataBar,
      }
    },
    methods: {
      setTab(name) {
        this.currentTab = name
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
