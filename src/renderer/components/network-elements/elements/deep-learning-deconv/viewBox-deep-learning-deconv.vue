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
      //&& chartData['Weights&Output']
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Output'")
      .statistics-box_row
        .statistics-box_col(v-if="!testIsOpen")
          chart-heatmap(
          chartLabel="Weights"
          :chartData="chartData['Weights&Output'].Weights"
          )
        .statistics-box_col
          chart-picture(
          chartLabel="Output"
          :chartData="chartData['Weights&Output'].Output"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Bias'")
      .statistics-box_row
        chart-base(
        chartLabel="Bias"
        :chartData="chartData.Bias.Bias"
        )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Gradients'")
      chart-base(
      chartLabel="Bias"
      :chartData="chartData.Gradients.Gradients"
      :customColor="colorList"
      )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartPicture from "@/components/charts/chart-picture.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDeepLearningDeconv",
    components: {ChartBase, ChartHeatmap, ChartPicture},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartDataDefault: {
          'Weights&Output': {
            Weights: null,
            Output: null,
          },
          Bias: {
            Bias: null,
          },
          Gradients: {
            Gradients: null,
          }},
        currentTab: 'Weights & Output',
        tabset: ['Weights & Output', 'Bias', 'Gradients'],
        colorList: ['#83c1ff', '#0070d6', '#6b8ff7']
      }
    },
    methods: {
      setTab(name) {
        this.currentTab = name;
        this.setTabAction();
      },
      getData() {
        let name = this.currentTab;
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
        this.chartRequest(this.boxElementID, 'DeepLearningDeconv', 'Weights&Output')
      },
      getWeightsStatistics() {
        this.chartRequest(this.boxElementID, 'DeepLearningDeconv', 'Bias')
      },
      getGradientsStatistics() {
        this.chartRequest(this.boxElementID, 'DeepLearningDeconv', 'Gradients')
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
