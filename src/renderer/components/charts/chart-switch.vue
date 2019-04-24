<template lang="pug">
    component(
      v-if="imgType.length"
      :is="componentName"
      :chart-label="chartLabel"
      :disable-header="disableHeader"
      :chart-data="imgData"
    )
</template>

<script>
  import ChartPicture from "@/components/charts/chart-picture";
  import ChartBase    from "@/components/charts/chart-base";
  import ChartHeatmap from "@/components/charts/chart-heatmap";
  export default {
    name: "ChartSwitch",
    components: { ChartHeatmap, ChartBase, ChartPicture },
    props: {
      chartLabel: {
        type: String,
        default: ''
      },
      chartData: {
        type: [Object, Array],
        default: function () {
          return null
        }
      },
      // customColor: {
      //   type: Array,
      //   default: function () {
      //     return []
      //   }
      // },
      disableHeader: {
        type: Boolean,
        default: false
      },
    },
    data() {
      return {
        imgType: '',
        imgData: null
      }
    },
    computed: {
      componentName() {
        let imgType = this.imgType;
        if(imgType === 'rgba')                                                return 'ChartPicture';
        if(imgType === 'line' || imgType === 'bar' || imgType === 'scatter')  return 'ChartBase';
        if(imgType === 'heatmap')                                             return 'ChartHeatmap';
      }
    },
    watch: {
      chartData(newVal) {
        if(newVal) {
          this.imgType = newVal.series[0].type;
          this.imgData = newVal;
        }
        else {
          this.imgType = '';
          this.imgData = null
        }
        // if(Array.isArray(newVal)) {
        //   // let type = newVal[0].type;
        //   // this.imgType = type;
        //   // if( type === 'rgba') this.imgData = newVal;
        // }
        // else {
        //
        // }
      }
    },
  }
</script>
