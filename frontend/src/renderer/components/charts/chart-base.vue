<template lang="pug">
  v-chart(
    ref="chart"
    :auto-resize="true"
    :options="chartModel"
    :theme="currentTheme"
  )
</template>

<script>
  import {pathWebWorkers}     from '@/core/constants.js'
  import chartMixin           from "@/core/mixins/charts.js";
  import { mapState } from 'vuex';
  import { THEME_DARK, THEME_LIGHT } from '@/core/constants.js';

  export default {
    name: "ChartBase",
    mixins: [chartMixin],
    data() {
      return {
        defaultModel: {
          tooltip: {
            show: true,
            confine: true,
            trigger: 'axis',
            backgroundColor: '#475D9C',
            textStyle: {
              fontSize: 10
            }
          },
          toolbox: {
            feature: {
              saveAsImage: {
                title: 'Save',
                show: false
              },
            }
          },
          grid: {
            left: '3%',
            bottom: '7%',
            top: '30px',
            right: '3%',
            containLabel: true
          },
          xAxis: {
            data: [],
            axisLabel: {
              showMinLabel: true,
              showMaxLabel: true
            }
          },
          yAxis: {
            nameTextStyle: {
              fontSize: 10
            }
          },
          legend: {},
          series: [],
          dataZoom: [{
            type: 'inside',
            throttle: 50,
            moveOnMouseMove: false
          }]
        }
      }
    },
    props: {
      enableDrag: {
        type: Boolean,
        default: true
      },
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
        this.wWorker = new Worker(`${pathWebWorkers}/calcChartBase.js`, {type: 'module'});
        this.wWorker.addEventListener('message', this.drawChart, false);
      },
      sendDataToWWorker(dataWatch) {
        let data = dataWatch || this.chartData;
        this.defaultModel.dataZoom[0].moveOnMouseMove = this.enableDrag;
        if (data === null || data === undefined) {
          this.chartModel = this.defaultModel;
          return
        }
        let model = {...this.defaultModel, ...data};
        let typeChart = model.series[0].type;
        if(typeChart === 'bar') {
          model.xAxis.boundaryGap = true;
          model.legend.type = "scroll";
        }
        this.wWorker.postMessage({
          model,
          xLength: data.xLength
        });
      }
    },
  }
</script>
