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
    chart-switch.data-settings_chart(
      v-if="shouldShowPreview"
      :disable-header="true"
      :chart-data="storeCurrentElement.chartData"
    )

</template>

<script>
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import SettingInputs  from "@/components/network-elements/elements-settings/setting-inputs.vue";
  import SettingOutputs  from "@/components/network-elements/elements-settings/setting-outputs.vue";
  import {mapActions, mapGetters} from 'vuex';
  
export default {
  name: "SettingsPreview",
  inject: ['hideAllWindow'],
  components: {ChartSwitch, SettingInputs, SettingOutputs},
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
        isTutorialMode:       'mod_tutorials/getIstutorialMode',
    }),
    layerId() {
      return this.currentEl.layerId
    },
    storeCurrentElement() {
      return this.$store.getters['mod_workspace/GET_networkElementById'](this.layerId);
    },
    eLConnectionInElementChartData() {
      return this.$store.getters['mod_workspace/GET_networkElementConnectionInChartData'](this.layerId);
    },
    shouldShowPreview() {
      return this.storeCurrentElement.chartData && this.storeCurrentElement.chartData.series && this.storeCurrentElement.chartData.series[0].data !== ''
    }
  },
  methods: {
    ...mapActions({
      api_getVariableList:  'mod_api/API_getPreviewVariableList',
      api_getPreviewSample: 'mod_api/API_getPreviewSample',
      api_getOutputDim:     'mod_api/API_getOutputDim',
      tutorialPointActivate:'mod_tutorials/pointActivate',
    }),
    toSettings() {
      this.$emit('to-settings');
    },
    confirmSettings() {
      this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-confirm'});
      this.hideAllWindow();
    },
    getSample(variableName) {
      this.api_getPreviewSample({layerId: this.layerId, varData: variableName})
        .then((data)=> {
          this.previewValue = variableName;
          this.imgData = data;
          this.$store.dispatch('mod_workspace/SET_NeteworkChartData', { 
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
            previewVarialbeName: data.VariableName,
          });
          this.$store.commit('mod_workspace/SET_previewVariableList', {
            layerId: this.layerId,
            previewVariableList: data.VariableList,
          });

        })
    },
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
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
    width: 145px;
    box-sizing: border-box;
    border: 1px solid #3F4C70;
    border-radius: 0 0 4px 4px;
  }
  .network-component-footer-wrapper {
    display: flex;
    justify-content: space-between;
    background: #23252A;
    border-bottom: 1px solid #3F4C70;
    &.no-preview {
      border-bottom: 1px solid transparent;
    }
  }
 
  .data-settings_chart {
    border-radius:  0 0 4px 4px;
  }
</style>
