<template lang="pug">
  .settings-layer
    .network-component-footer-wrapper(:class="{ 'no-preview': !(shouldShowPreview) }")
      setting-inputs(
        :element="storeCurrentElement"
      )
      setting-outputs(
        :element="storeCurrentElement"
        :outputsVariables="storeCurrentElement.previewVariableList"
      )
    .chart-spinner-wrapper(v-if="showLoadingSpinner")
      chart-spinner(:invert="true")
    .chart-container(v-if="!showLoadingSpinner" style="overflow: hidden")
      transition(name="slide-fade")
        chart-switch.data-settings_chart(
          v-show="shouldShowPreview"
          :disable-header="true"
          :chart-data="storeCurrentElement.chartData"
          :showInitiallyRequestSpinner="false"
          :chartIdx="currentEl.chartIdx"
          @chartIdxChange="handleChartIdxChange"
          :enableDrag="enableDrag"
          :invert-theme="true"
        )

</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import SettingInputs  from "@/components/network-elements/elements-settings/setting-inputs.vue";
  import SettingOutputs  from "@/components/network-elements/elements-settings/setting-outputs.vue";
  import ChartSpinner     from '@/components/charts/chart-spinner'
  import {mapActions, mapGetters} from 'vuex';
  
export default {
  name: "SettingsPreview",
  inject: ['hideAllWindow'],
  components: {ChartSwitch, SettingInputs, SettingOutputs, ChartSpinner},
  props: {
    currentEl: { type: Object },
  },
  data() {
    return {
      // previewValue: 'output',
      previewList: [],
      imgData: null,
      haveChartToDisplay: false
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:          'mod_tutorials/getIsTutorialMode',
      statisticsOrTestIsOpen:  'mod_workspace/GET_statisticsOrTestIsOpen',
    }),
    enableDrag() {
      if(this.statisticsOrTestIsOpen) return true;
      return false;
    },
    showLoadingSpinner() {
      return this.storeCurrentElement.chartDataIsLoading !== undefined && this.storeCurrentElement.chartDataIsLoading !== 0;
    },
    layerId() {
      return this.currentEl.layerId
    },
    storeCurrentElement() {
      if (this.statisticsOrTestIsOpen) {
        return this.$store.getters['mod_workspace/GET_networkSnapshotElementById'](this.layerId);
      } else {
        return this.$store.getters['mod_workspace/GET_networkElementById'](this.layerId);
      }
    },
    eLConnectionInElementChartData() {
      return this.$store.getters['mod_workspace/GET_networkElementConnectionInChartData'](this.layerId);
    },
    showModelPreviews() {
      return this.$store.state.mod_workspace.showModelPreviews;
    },
    shouldShowPreview() {
      return (this.storeCurrentElement && this.storeCurrentElement.chartData && this.storeCurrentElement.chartData.series && this.storeCurrentElement.chartData.series[0].data !== '')
      && !this.statisticsOrTestIsOpen
      && this.showModelPreviews;
    },
  },
  methods: {
    ...mapActions({
      api_getVariableList:  'mod_api/API_getPreviewVariableList',
      api_getPreviewSample: 'mod_api/API_getPreviewSample',
      api_getOutputDim:     'mod_api/API_getOutputDim',
    }),
    toSettings() {
      this.$emit('to-settings');
    },
    confirmSettings() {
      this.hideAllWindow();
    },
    getSample(variableName) {
      this.api_getPreviewSample({layerId: this.layerId, varData: variableName})
        .then((data)=> {
          this.previewValue = variableName;
          this.imgData = data;
          this.$store.dispatch('mod_workspace/SET_NetworkChartData', { 
            layerId: this.layerId,
            payload: data,
          });

          this.$store.dispatch('mod_events/EVENT_calcArray');
        });
    },
    getVariableList() {
      this.api_getVariableList(this.layerId)
        .then((data)=> {
          this.$store.commit('mod_workspace/SET_previewVariable', {
            layerId: this.layerId,
            previewVariableName: data.VariableName,
          });
          this.$store.commit('mod_workspace/SET_previewVariableList', {
            layerId: this.layerId,
            previewVariableList: data.VariableList,
          });

        })
    },
    handleChartIdxChange(chartIdx) {
      this.$store.dispatch('mod_workspace/SET_NetworkChartIdx', { 
        layerId: this.layerId,
        payload: chartIdx,
      });
    }
  }
}
</script>
<style lang="scss" scoped>
  
  .settings-layer_foot {
    justify-content: flex-end;
    .btn + .btn {
      margin-left: .8rem;
    }
  }
  .settings-layer_section {
    width: 142px;
  }
  .settings-layer {
    width: 150px;
    box-sizing: border-box;
    border-radius: 0 0 4px 4px;
  }
  .network-component-footer-wrapper {
    display: flex;
    justify-content: space-between;
    background: $bg-setting-layer;
    border-bottom: 1px solid #3F4C70;
    &.no-preview {
      border-bottom: 1px solid transparent;
      border-radius: 0 0 4px 4px;
    }
  }
 
  .data-settings_chart {
    border-radius:  0 0 4px 4px;
  }

  .chart-container {
    height: 14rem;
  }

  .chart-spinner-wrapper {
    position: relative;
    background: $bg-setting-layer;
    min-height: 140px;
    .chart-spinner-box {
      background: transparent;
    }
  }
  .slide-fade-enter-active {
    transition: all 1s ease;
  }
  .slide-fade-enter {
    transition-duration: 2s;
    transform: translateY(-140px);
  }

  .slide-fade-leave-to {
    transition-duration: 0.7s;
    transform: translateY(-140px);
  }

</style>
