<template lang="pug">
  .statistics-box.statistics-box--horizontally
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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Output'")
      .statistics-box_row
        .statistics-box_col(v-if="!testIsOpen")
          chart-heatmap(
            key="1"
            chart-label="Weights"
            :chart-data="chartData['Weights&Output'].Weights"
            )
        .statistics-box_col
          chart-picture(
            key="2"
            chart-label="Output"
            :chart-data="chartData['Weights&Output'].Output"
            )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Bias'")
      .statistics-box_row
        chart-base(
          key="3"
          chart-label="Bias"
          :chart-data="chartData.Bias.Bias"
        )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Gradients'")
      chart-base(
        key="4"
        chart-label="Bias"
        :chart-data="chartData.Gradients.Gradients"
        :custom-color="colorList"
      )
      //-.statistics-box_row
        chart-base(
        chartLabel="Min"
        /:chartData="chartData.Gradients.Min"
        )
        chart-base(
        chartLabel="Max"
        /:chartData="chartData.Gradients.Max"
        )
      //-.statistics-box_row
        chart-base(
        chartLabel="Average"
        -:chartData="chartData.Gradients.Average"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import ChartPicture from "@/components/charts/chart-picture.vue";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDeepLearningConv",
    components: {ChartBase, ChartHeatmap, ChartPicture},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
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
        switch (this.currentTab) {
          case 'Weights & Output':
            this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Weights&Output')
            break;
          case 'Bias':
            this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Bias')
            break;
          case 'Gradients':
            this.chartRequest(this.boxElementID, 'DeepLearningConv', 'Gradients')
            break;
        }
      }
    }
  }
</script>
