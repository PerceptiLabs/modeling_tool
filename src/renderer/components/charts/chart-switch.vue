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
        if(imgType === 'image' || imgType === 'RGB' || imgType === 'grayscale') return 'ChartPicture';
        if(imgType === 'line' || imgType === 'bar' || imgType === 'scatter') return 'ChartBase';
        if(imgType === 'heatmap') return 'ChartHeatmap';
      }
    },
    watch: {
      chartData(newVal) {
        if(Array.isArray(newVal)) {
          let type = newVal[0].type;
          this.imgType = type;
          if( type === 'image' || type === 'RGB' || type === 'grayscale') this.imgData = newVal;
        }
        else {
          let type = newVal.series[0].type;
          this.imgType = type;
          if( type === 'image' || type === 'RGB' || type === 'grayscale') this.imgData = newVal.series; //TODO привести к единому виду
          else this.imgData = newVal;
        }
      }
    },
    methods: {

    },
  }
</script>
