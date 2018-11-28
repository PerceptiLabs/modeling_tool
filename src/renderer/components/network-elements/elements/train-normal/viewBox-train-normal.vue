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
        :disabled="i > 2"
        ) {{ tab }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row
        .statistics-box_col
          chart-line(
            :chartData="prediction.Input"
            )
      .statistics-box_row
        .statistics-box_col
          chart-line(
          :chartData="prediction.PvG"
          )
        .statistics-box_col
          chart-line(
          :chartData="prediction.AveragePvG"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-line(
        chartLabel="Accuracy during one epoch"
        :chartData="accuracy.Current"
      )
      chart-line(
        chartLabel="Accuracy over all epochs"
        :chartData="accuracy.Total"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-line(
      chartLabel="Loss during one epoch"
      /:chartData="optionLine1"
      )
      chart-line(
      chartLabel="Loss over all epochs"
      /:chartData="optionLine1"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'F1'")
      chart-line(
      chartLabel="F1 during one epoch"
      /:chartData="optionLine1"
      )
      chart-line(
      chartLabel="F1 over all epochs"
      /:chartData="optionLine1"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'Precision & Recall'")
      chart-line(
      /:chartData="optionLine1"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'ROC'")
      chart-line(
      /:chartData="optionLine1"
      )
</template>

<script>
  import ChartLine    from "@/components/charts/chart-lineBar";
  import ChartHeatmap from "@/components/charts/chart-heatmap.vue";
  import ChartD3      from "@/components/charts/chart-3d.vue";
  import data3d       from "@/components/charts/3d.js";
  import dataHeat     from "@/components/charts/hear.js";
  import dataBar      from "@/components/charts/bar.js";
  import dataLine     from "@/components/charts/line.js";

  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxTrainNormal",
    components: {ChartLine, ChartHeatmap, ChartD3},
    mixins: [viewBoxMixin],
    data() {
      return {
        currentTab: 'Prediction',
        tabset: ['Prediction', 'Accuracy', 'Loss', 'F1', 'Precision & Recall', 'ROC'],
        //tabset: ['Prediction', 'Accuracy', 'Loss'],
        prediction: {
          Input: null,
          PvG: null,
          AveragePvG: null
        },
        accuracy: {
          Current: null,
          Total: null
        }
      }
    },
    methods: {
      setTab(name) {
        clearInterval(this.idTimer);
        this.currentTab = name;
        if(name === 'Prediction') {
          this.getStatistics()
        }
        else if (name === 'Accuracy') {
          this.getAccStatistics()
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
              layerId:'5',
              layerType:'Train',//FC
              view:'Prediction' //Output, Weights&Bias
            }
          };
          //console.log(theData);
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              let jsnData = JSON.parse(data);
              console.log(jsnData);
              this.prediction = jsnData
            })
            .catch((err) =>{
              console.error(err);
              clearInterval(this.idTimer);
            });
        }, 1000)
      },
      getAccStatistics() {
        this.idTimer = setInterval(()=>{
          //console.log('getOutStatistics');
          let theData = {
            reciever: 'Network',
            action: 'getLayerStatistics',
            value: {
              //layerId: this.elementID.toString(),
              layerId:'5',
              layerType:'Train',//FC
              view:'Accuracy' //Output, Weights&Bias
            }
          };
          //console.log(theData);
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              //console.log(data);
              //let jsnData = JSON.parse(data);

              //console.log(jsnData);
              console.log(data);
              this.accuracy = data
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
