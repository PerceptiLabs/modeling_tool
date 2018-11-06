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
    .statistics-box_main(v-show="currentTab === 'Output'")
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine1"
      )
    .statistics-box_main(v-show="currentTab === 'Weights & Bias'")
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine2"
      )
      chart-line(
      chartLabel="Accuracy over all epochs"
      :chartData="optionLine3"
      )
    .statistics-box_main(v-show="currentTab === 'Gradients'")
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
  import ChartLine from "@/components/charts/chart-line";
  export default {
    name: "ViewBoxLearnDeepConnect",
    components: {ChartLine},
    data() {
      return {
        currentTab: 'Output',
        tabset: ['Output', 'Weights & Bias', 'Gradients'],
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
        optionLine2: {
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
        optionLine3: {
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
        optionLine4: {
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
        optionLine5: {
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
        optionLine6: {
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
