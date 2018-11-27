<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine"
        )
</template>

<script>
  import ChartLine    from "@/components/charts/chart-lineBar.vue";
  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxProcessHot",
    components: {ChartLine},
    mixins: [viewBoxMixin],
    data() {
      return {
        optionLine: null,
      }
    },
    methods: {
      getStatistics() {
        this.idTimer = setInterval(()=>{
          //console.log('ProcessHot Statistics');
          let theData = {
            reciever: 'Network',
            action: 'getLayerStatistics',
            value: {
              //layerId: this.elementID.toString(),
              layerId:'4',
              layerType:'OneHot',
              view:''
            }
          };
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              let jsnData = JSON.parse(data);
              this.optionLine = jsnData.Output
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        }, this.timeInterval)
      },
    }
  }
</script>

<style lang="scss" scoped>

</style>
