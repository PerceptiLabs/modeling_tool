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
      chart-base(
        chartLabel="Bias"
        :chartData="chartData.Gradients.Gradients"
        :customColor="colorList"
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
            this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Output')
            break;
          case 'Weights & Bias':
            this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Weights&Bias')
            break;
          case 'Gradients':
            this.chartRequest(this.boxElementID, 'DeepLearningRecurrent', 'Gradients')
            break;
        }
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
