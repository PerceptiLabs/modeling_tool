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
    .statistics-box_main.statistics-box_col(v-show="currentTab === 'Weights & Output'")
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-show="currentTab === 'Bias'")
      chart-line(
      chartLabel="Accuracy over all epochs"
      :chartData="optionLine3"
      )
    .statistics-box_main.statistics-box_col(v-show="currentTab === 'Gradients'")
      .statistics-box_row
        chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine4"
        )
        chart-line(
        chartLabel="Accuracy over all epochs"
        :chartData="optionLine5"
        )
      chart-line(
        chartLabel="Accuracy over all epochs"
        :chartData="optionLine6"
      )
</template>

<script>
  import ChartLine from "@/components/charts/chart-lineBar";
  import dataLine     from "@/components/charts/line.js";
  export default {
    name: "ViewBoxLearnDeepRecurrent",
    components: {ChartLine},
    data() {
      return {
        currentTab: 'Gradients',
        tabset: ['Weights & Output', 'Bias', 'Gradients'],
        optionLine1: dataLine,
        optionLine2: dataLine,
        optionLine3: dataLine,
        optionLine4: dataLine,
        optionLine5: dataLine,
        optionLine6: dataLine,
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
