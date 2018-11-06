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
    .statistics-box_main(v-if="currentTab === 'Prediction'")
    .statistics-box_main(v-if="currentTab === 'Accuracy'")
      chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine1"
      )
      chart-line(
        chartLabel="Accuracy over all epochs"
        :chartData="optionLine1"
      )
    .statistics-box_main(v-if="currentTab === 'Loss'")
    .statistics-box_main(v-if="currentTab === 'F1'")
    .statistics-box_main(v-if="currentTab === 'Precision & Recall'")
    .statistics-box_main(v-if="currentTab === 'ROC'")
</template>

<script>
import ChartLine from "../charts/chart-line";
export default {
  name: "StatisticsOutNormal",
  components: {ChartLine},
  data() {
    return {
      currentTab: '',
      tabset: ['Prediction', 'Accuracy', 'Loss', 'F1', 'Precision & Recall', 'ROC'],
      optionLine1: {
        tooltip: {},
        xAxis: {
          data: ['Geek', 'Potato', 'Cool', 'Cat', 'Dog'],
        },
        yAxis: {},
        series: [
          {
            type: 'line',
            data: [0.1, 0.5, 0.6, .99, .75],
          },
          {
            type: 'line',
            data: [0.51, 0.15, 0.96, .199, .175],
          }
        ]
      },
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
