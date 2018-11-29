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
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output'")
      chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="chartOutput"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Bias'")
      chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="chartWnB.Weights"
      )
      chart-base(
        chartLabel="Accuracy over all epochs"
        :chartData="chartWnB.Bias"
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
        chartOutput: null,
        chartWnB: {
          Weights: null,
          Bias: null
        }
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
        this.idTimer = setInterval(()=>{
          let theData = this.returnDataRequest(this.boxElementID, 'FC', 'Output');
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              this.chartOutput = data.Output
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        }, this.timeInterval)
      },
      getWeightsStatistics() {
        this.idTimer = setInterval(()=>{
          const client = new requestApi();
          let theData = this.returnDataRequest(this.boxElementID, 'FC', 'Weights&Bias');
          client.sendMessage(theData)
            .then((data)=> {
              this.chartWnB = data;
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        }, this.timeInterval)
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
