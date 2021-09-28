<template lang="pug">
  v-chart(
    ref="chart"
    :auto-resize="true"
    :options="chartModel"
    :theme="currentTheme"
  )
</template>

<script>
  import chartMixin       from "@/core/mixins/charts.js";
  import { mapState } from 'vuex';
  import { THEME_DARK, THEME_LIGHT } from '@/core/constants.js';

  export default {
    name: "ChartPie",
    mixins: [chartMixin],
    data() {
      return {
        defaultModel: {
          tooltip: {
            show: true,
            confine: true,
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
          series: []
        },
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

      },
      sendDataToWWorker(dataWatch) {
        let data = dataWatch || this.chartData;
        if (!data) {
          this.chartModel = this.defaultModel;
          return
        }
        let model = {...this.defaultModel, ...data};
        let currentData = model.series[0];
        let addOptions = {
          label: {
            normal: { show: false },
            emphasis: { show: false }
          },
          lableLine: {
            normal: { show: false },
            emphasis: { show: false }
          },
        };
        model.series[0] = {...currentData, ...addOptions};
        this.drawChart({data: model});

      }
    },
  }
</script>


