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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Gradients' && chartData.Gradients")
      .statistics-box_row
        chart-base(
        chartLabel="Min"
        :chartData="chartData.Gradients.Min"
        )
        chart-base(
        chartLabel="Max"
        :chartData="chartData.Gradients.Max"
        )
      .statistics-box_row
        chart-base(
        chartLabel="Average"
        :chartData="chartData.Gradients.Average"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDeepLearningRecurrent",
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
        else if (name === 'Gradients') {
          this.getGradientsStatistics()
        }

      },
      getStatistics() {
        this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Output')
      },
      getWeightsStatistics() {
        this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Weights&Bias')
      },
      getGradientsStatistics() {
        this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Gradients')
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
