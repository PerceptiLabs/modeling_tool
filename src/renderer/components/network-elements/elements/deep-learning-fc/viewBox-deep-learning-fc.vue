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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output'")
      chart-base(
        key="1"
        chart-label="Value"
        :chart-data="chartData.Output.Output"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Bias'")
      chart-base(
        key="2"
        chart-label="Weights"
        :chart-data="chartData['Weights&Bias'].Weights"
      )
      chart-base(
        key="3"
        chart-label="Bias"
        :chart-data="chartData['Weights&Bias'].Bias"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Gradients'")
      chart-base(
        key="4"
        chart-label="Gradients"
        :chart-data="chartData.Gradients.Gradients"
        :custom-color="colorList"
      )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDeepLearningFC",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Output: {
            Output: null,
          },
          'Weights&Bias': {
            Weights: null,
            Bias: null,
          },
          Gradients: {
            Gradients: null,
          }
        },
        currentTab: 'Output',
        tabset: ['Output', 'Weights & Bias', 'Gradients'],
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
          case 'Output':
            this.chartRequest(this.boxElementID, 'DeepLearningFC', 'Output')
            break;
          case 'Weights & Bias':
            this.chartRequest(this.boxElementID, 'DeepLearningFC', 'Weights&Bias')
            break;
          case 'Gradients':
            this.chartRequest(this.boxElementID, 'DeepLearningFC', 'Gradients')
            break;
        }
      }
    }
  }
</script>
