<template lang="pug">
  .sidebar-setting-preview(v-if="storeCurrentElement.chartData && storeCurrentElement.chartData.series && storeCurrentElement.chartData.series[0].data !== ''")
    div(
      @click="toggleSettingPreviewVisibility()"
    )
      h4.sidebar-setting-preview-title Preview
      .preview-chevron(:class="{'is-open': isSettingPreviewVisible}")
    chart-switch.data-settings_chart(
      v-if="!isSettingPreviewVisible"
      :disable-header="true"
      :chart-data="storeCurrentElement.chartData"
    )
</template>

<script>
  //import codeHq    from "@/components/network-elements/elements-settings/code-hq.vue";
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import {mapActions, mapGetters} from 'vuex';
export default {
  name: "SidebarSettingPreview",
  inject: [],
  components: {ChartSwitch},
  props: {
    currentEl: { type: Object },
  },
  mounted () {
  //  this.getSample();
  },
  data() {
    return {
      previewValue: '',
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
    isSettingPreviewVisible() {
      return this.$store.state.mod_workspace.isSettingPreviewVisible;
    }
  },
  watch: {
    // previewValue(newVal, prevValuel) {
    //   if(newVal !== prevValuel) {
    //     this.getSample(newVal);
    //   }
    // },
    // layerId() {
    //   this.getSample(this.previewValue);
    // },
  },
  methods: {
    ...mapActions({
      api_getVariableList:  'mod_api/API_getPreviewVariableList',
      api_getPreviewSample: 'mod_api/API_getPreviewSample',
      api_getOutputDim:     'mod_api/API_getOutputDim',
      tutorialPointActivate:'mod_tutorials/pointActivate',
    }),
    toggleSettingPreviewVisibility() {
      this.$store.commit('mod_workspace/toggleSettingPreviewVisibility');
    },
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
        })
    },
    // getVariableList() {
    //   this.api_getVariableList(this.layerId)
    //     .then((data)=> {
    //       this.previewValue = data.VariableName;
    //       this.previewList = data.VariableList.length ? data.VariableList : [];
    //     })
    // },
    haveData(){
      this.haveChartToDisplay = this.storeCurrentElement.chartData.series && this.storeCurrentElement.chartData.series[0].data !== '';
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
  .sidebar-setting-preview {
    padding: 7px 5px 14px 10px
  }
  .sidebar-setting-preview-title {
    display: inline-block;
    cursor: pointer;
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 300;
    font-size: 9px;
    line-height: 12px;
    margin-bottom: 0;
  }
  .preview-chevron {
    cursor: pointer;
    margin-left: 5px;
    display: inline-block;
    border-top: 4px solid #ccc;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    &.is-open {
      border-top: none;
      border-bottom: 4px solid #ccc;
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
    }
  }
  
</style>
