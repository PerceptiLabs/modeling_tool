<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-line(
      chartLabel="Accuracy during one epoch"
      :chartData="optionLine1"
      )
</template>

<script>
  import ChartLine from "@/components/charts/chart-line";
  import dataLine  from "@/components/charts/line.js";
  import requestApi  from "@/core/api.js";
  export default {
    name: "ViewBoxDataData",
    components: {ChartLine},
    mounted() {
      setTimeout(()=>{
        var theData = {
          reciever: rootGetters['mod_workspace/currentNetwork'].networkName,
          action: "getLayerStatistics",
          value: {
            layerId:"1",
            layerType:"Data",//FC
            view:"" //Output, Weights&Bias
          }
        };
        this.requestApi(theData)
      }, 1000)
    },
    data() {
      return {
        optionLine1: dataLine,
      }
    },
    method: {
      requestApi
    }
  }
</script>

<style lang="scss" scoped>

</style>
