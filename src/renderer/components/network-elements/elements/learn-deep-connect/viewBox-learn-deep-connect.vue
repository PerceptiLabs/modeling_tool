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
        ) {{ tab }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Output'")
      chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Weights & Bias'")
      chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="optionLine2"
      )
      chart-line(
        chartLabel="Accuracy over all epochs"
        :chartData="optionLine3"
      )
    //.statistics-box_main.statistics-box_col(v-show="currentTab === 'Gradients'")
      .statistics-box_row
        chart-line(
        chartLabel="Accuracy during one epoch"
        /:chartData="optionLine4"
        )
        chart-line(
        chartLabel="Accuracy over all epochs"
        /:chartData="optionLine5"
        )
      .statistics-box_row
        chart-line(
        chartLabel="Accuracy over all epochs"
        /:chartData="optionLine6"
        )
</template>

<script>
  import ChartLine  from "@/components/charts/chart-lineBar.vue";
  import requestApi from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxLearnDeepConnect",
    components: {ChartLine},
    mixins: [viewBoxMixin],
    data() {
      return {
        currentTab: 'Output',
        tabset: ['Output', 'Weights & Bias', 'Gradients'],
        optionLine1: null,
        optionLine2: null,
        optionLine3: null,
        // optionLine4: dataLine,
        // optionLine5: dataLine,
        // optionLine6: dataLine,
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
          //console.log('getOutStatistics');
          let theData = {
            reciever: 'Network',
            action: 'getLayerStatistics',
            value: {
              //layerId: this.elementID.toString(),
              layerId:'2',
              layerType:'FC',//FC
              view:'Output' //Output, Weights&Bias
            }
          };
          //console.log(this.elementID.toString());
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              let jsnData = JSON.parse(data);
              this.optionLine1 = jsnData.Output
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        }, 1000)
      },
      getWeightsStatistics() {
        this.idTimer = setInterval(()=>{
          //console.log('getWeightsStatistics');
          const client = new requestApi();
          const theData = {
            reciever: 'Network',
            action: "getLayerStatistics",
            value: {
              //layerId: this.elementID.toString(),
              layerId:"2",
              layerType:"FC",//FC
              view:"Weights&Bias" //Output, Weights&Bias
            }
          };
          client.sendMessage(theData)
            .then((data)=> {
              let jsnData = JSON.parse(data);
              this.optionLine2 = jsnData.Weights;
              this.optionLine3 = jsnData.Bias;
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        }, 1000)
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
