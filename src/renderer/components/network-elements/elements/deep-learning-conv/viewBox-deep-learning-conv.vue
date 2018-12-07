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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Output' && chartData['Weights&Output']")
      chart-heatmap(
        chartLabel="Weights"
        :chartData="chartData['Weights&Output'].Weights"
        )
      //chart-base(
        chartLabel="Bias"
        /:chartData="chartData['Output&Bias'].Output"
        )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Bias' && chartData.Bias")
      .statistics-box_row
        chart-base(
        chartLabel="Bias"
        :chartData="chartData.Bias.Bias"
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
  import ChartBase    from "@/components/charts/chart-base";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDeepLearningConv",
    components: {ChartBase, ChartHeatmap},
    mixins: [viewBoxMixin],
    data() {
      return {
        currentTab: 'Weights & Output',
        tabset: ['Weights & Output', 'Bias', 'Gradients'],
      }
    },
    methods: {
      setTab(name) {
        clearInterval(this.idTimer);
        this.currentTab = name;
        if(name === 'Weights & Output') {
          this.getStatistics()
        }
        else if (name === 'Bias') {
          this.getWeightsStatistics()
        }
        else if (name === 'Gradients') {
          this.getGradientsStatistics()
        }

      },
      getStatistics() {//not Weights
        this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Weights&Output')
      },
      getWeightsStatistics() {
        this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Bias')
      },
      getGradientsStatistics() {
        this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Gradients')
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
