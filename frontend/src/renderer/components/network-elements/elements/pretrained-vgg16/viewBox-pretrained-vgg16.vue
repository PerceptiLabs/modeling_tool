<template lang="pug">
  .statistics-box.statistics-box--horizontally
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output'")
      chart-switch(
        key="1"
        chart-label="Value"
        :chart-data="chartData.Output.Output"
      )
</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxPreTrainedVGG16",
    components: { ChartSwitch },
    mixins: [ viewBoxMixin ],
    data() {
      return {
        chartData: {
          Output: {
            Output: null,
          }
        },
        btnList: {'Output': null},
        colorList: ['#83c1ff', '#0070d6', '#6b8ff7']
      }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Output':
            this.chartRequest(this.boxElementID, 'PreTrainedVGG16', 'Output');
            break;
        }
      }
    }
  }
</script>
