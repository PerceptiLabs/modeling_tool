<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      //chart-line(
        chartLabel="Accuracy during one epoch"
        /:chartData="optionLine1"
        )
</template>

<script>
  import ChartLine    from "@/components/charts/chart-line";
  import dataLine     from "@/components/charts/line.js";
  import requestApi   from "@/core/api.js";
  export default {
    name: "ViewBoxDataData",
    components: {ChartLine},
    mounted() {
      //this.getStatistics()
    },
    data() {
      return {
        optionLine1: dataLine,
      }
    },
    computed: {
      elementID() {
        let viewBoxEl = this.$store.getters['mod_workspace/currentSelectedEl'].find((element)=>element.el.layerType !== 'Training');
        return viewBoxEl.el.layerId
      },
      currentNetworkName() {
        return this.$store.getters['mod_workspace/currentNetwork'].networkName
      }
    },
    methods: {
      getStatistics() {
        var theData = {
          reciever: this.currentNetworkName,
          action: "getLayerStatistics",
          value: {
            layerId: this.elementID.toString(),
            //layerId: "1",
            layerType: "Data",//FC
            view:"" //Output, Weights&Bias
            // layerId: "2",
            // layerType: "FC",//
            // view:"Output" //, Weights&Bias
          }
        };
        setInterval(()=>{
          console.log(this.elementID.toString());
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> { console.log('promis', data.toString())})
            .catch((err) =>{ console.error(err); })
        }, 2000)
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
