<template lang="pug">
  v-chart(
    ref="chart"
    :auto-resize="true"
    :options="chartModel"
    :theme="currentTheme"
    )
</template>

<script>
import {pathWebWorkers} from '@/core/constants.js'
import chartMixin       from "@/core/mixins/charts.js";
import { mapState } from 'vuex';
import { THEME_DARK, THEME_LIGHT } from '@/core/constants.js';

export default {
  name: "ChartHeatmap",
  mixins: [chartMixin],
  data() {
    return {
      defaultModel: {
        tooltip: {
          show: true,
          backgroundColor: '#475D9C',
        },
        grid: {
          right: 50
        },
        xAxis: {
          boundaryGap: true,
          data: []
        },
        yAxis: {
          boundaryGap: true,
          data: []
        },
        visualMap: {
          min: 0,
          max: 1,
          top: '10px',
          itemHeight: 300,
          realtime: false,
          left: 'right',
        },
        series: []
      }
    }
  },
  props: {
    invert: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    ...mapState({
      theme:                      state => state.globalView.theme
    }),
    currentTheme () {
      if( this.invert ) {
        return this.theme === THEME_DARK ? THEME_LIGHT : THEME_DARK
      }
      return this.theme;
    }
  },
  methods: {
    createWWorker() {
      this.wWorker = new Worker(`${pathWebWorkers}/calcChartHeatMap.js`);
      this.wWorker.addEventListener('message', this.drawChart, false);
    },
    sendDataToWWorker(dataWatch) {
      let data = dataWatch || this.chartData;
      if (data === null || data === undefined) {
        this.chartModel = this.defaultModel;
        return
      }
      let model = {...this.defaultModel};
      model.series = data.series;
      this.wWorker.postMessage(model);
    }
  }
}
</script>