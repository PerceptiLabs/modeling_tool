<template lang="pug">
  .statistics-box
    button.btn.btn--link(type="button" @click="getWeightsStatistics") get stat
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
    .statistics-box_main.statistics-box_col(v-show="currentTab === 'Output'")
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-show="currentTab === 'Weights & Bias'")
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine2"
      )
      chart-line(
      chartLabel="Accuracy over all epochs"
      :chartData="optionLine3"
      )
    .statistics-box_main.statistics-box_col(v-show="currentTab === 'Gradients'")
      .statistics-box_row
        chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine4"
        )
        chart-line(
        chartLabel="Accuracy over all epochs"
        :chartData="optionLine5"
        )
      .statistics-box_row
        chart-line(
        chartLabel="Accuracy over all epochs"
        :chartData="optionLine6"
        )
</template>

<script>
  import ChartLine from "@/components/charts/chart-line";
  import dataLine  from "@/components/charts/line.js";
  import requestApi   from "@/core/api.js";
  export default {
    name: "ViewBoxLearnDeepConnect",
    components: {ChartLine},
    data() {
      return {
        currentTab: 'Output',
        tabset: ['Output', 'Weights & Bias', 'Gradients'],
        optionLine1: dataLine,
        optionLine2: dataLine,
        optionLine3: dataLine,
        optionLine4: dataLine,
        optionLine5: dataLine,
        optionLine6: dataLine,

      }
    },
    methods: {
      setTab(name) {
        this.currentTab = name
      },
      getOutStatistics() {
        var theData = {
          reciever: 'Network',
          action: "getLayerStatistics",
          value: {
            //layerId: this.elementID.toString(),
            layerId:"2",
            layerType:"FC",//FC
            view:"Output" //Output, Weights&Bias
          }
        };
        //console.log(this.elementID.toString());
        const client = new requestApi();
        client.sendMessage(theData)
          .then((data)=> {
            let jsn = JSON.parse(data);
            console.log(jsn);
            this.optionLine1 = jsn
          })
          .catch((err) =>{ console.error(err); })
        setInterval(()=>{

        }, 2000)
      },
      getWeightsStatistics() {
        var theData = {
          reciever: 'Network',
          action: "getLayerStatistics",
          value: {
            //layerId: this.elementID.toString(),
            layerId:"2",
            layerType:"FC",//FC
            view:"Weights&Bias" //Output, Weights&Bias
          }
        };
        //console.log(this.elementID.toString());
        const client = new requestApi();
        client.sendMessage(theData)
          .then((data)=> {
            let jsn = JSON.parse(data);
            console.log(jsn);
            console.log(this);
            this.optionLine2 = jsn.Weights;
            this.optionLine3 = jsn.Bias;
          })
          .catch((err) =>{ console.error(err); })
        setInterval(()=>{

        }, 2000)
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
