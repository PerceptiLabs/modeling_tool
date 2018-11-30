<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col
      chart-base(
        chartLabel="Accuracy during one epoch"
        :chartData="chartData.Output"
        )
</template>

<script>
  import ChartBase    from "@/components/charts/chart-base.vue";
  import requestApi   from "@/core/api.js";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxProcessHot",
    components: {ChartBase},
    mixins: [viewBoxMixin],
    mounted() {

    },
    data() {
      return {
        //Output: null
      }
    },
    computed: {
      // chartOutData() {
      //   console.log('chartOutData');
      //   if (this.$options.Output !== undefined) {
      //     return this.$options.Output
      //   } else return null
      // }
    },
    methods: {
      getStatistics() {
        this.chartRequest(this.boxElementID, 'OneHot', '');
        // this.idTimer = setInterval(()=>{
        //   let theData = this.returnDataRequest(this.boxElementID, 'OneHot', '');
        //   const client = new requestApi();
        //   client.sendMessage(theData)
        //     .then((data)=> {
        //       this.Output = data.Output;
        //     })
        //     .catch((err) =>{
        //       console.error(err);
        //       clearInterval(this.idTimer);
        //     });
        // }, this.timeInterval)
      },
    }
  }
</script>

<style lang="scss" scoped>

</style>
