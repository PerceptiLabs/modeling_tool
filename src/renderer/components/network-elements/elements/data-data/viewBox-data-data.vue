<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="Data"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base";
  import dataLine     from "@/components/charts/line.js";
  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
  export default {
    name: "ViewBoxDataData",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    mounted() {
      //this.getStatistics()
    },
    data() {
      return {
        Data: null
      }
    },
    computed: {
      // dataLine() {
      //   if(this.$option.line) {
      //     return this.$option.line
      //   }
      //   else return {
      //     Input: null,
      //   }
      // },
    },
    methods: {
      getStatistics() {
        this.idTimer = setInterval(()=>{
          let theData = this.returnDataRequest(this.boxElementID, 'Data', '');
          const client = new requestApi();
          client.sendMessage(theData)
            .then((data)=> {
              this.Data = data.Data
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
