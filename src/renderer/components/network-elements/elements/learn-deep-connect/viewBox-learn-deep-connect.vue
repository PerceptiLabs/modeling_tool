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
        :disabled="i > 1"
        ) {{ tab }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output' && chartData.Output")
      chart-base(
        chartLabel="Value"
        :chartData="chartData.Output.Output"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Bias' && chartData['Weights&Bias']")
      chart-base(
        chartLabel="Weights"
        :chartData="chartData['Weights&Bias'].Weights"
      )
      chart-base(
        chartLabel="Bias"
        :chartData="chartData['Weights&Bias'].Bias"
      )
    //.statistics-box_main.statistics-box_col(v-show="currentTab === 'Gradients'")
      .statistics-box_row
        chart-base(
        chartLabel="Accuracy during one epoch"
        /:chartData="optionLine4"
        )
        chart-base(
        chartLabel="Accuracy over all epochs"
        /:chartData="optionLine5"
        )
      .statistics-box_row
        chart-base(
        chartLabel="Accuracy over all epochs"
        /:chartData="optionLine6"
        )
</template>

<script>
  import ChartBase  from "@/components/charts/chart-base.vue";

  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxLearnDeepConnect",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    data() {
      return {
        currentTab: 'Output',
        tabset: ['Output', 'Weights & Bias', 'Gradients'],
      }
    },
    methods: {
      setTab(name) {
        clearInterval(this.idTimer);
        this.currentTab = name;
        if(name === 'Output') {
          this.getStatistics()
        }
        else if (name === 'Weights & Bias') {
          this.getWeightsStatistics()
        }

      },
      getStatistics() {
        this.chartRequest(this.boxElementID, 'FC', 'Output')
      },
      getWeightsStatistics() {
        this.chartRequest(this.boxElementID, 'FC', 'Weights&Bias')
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
