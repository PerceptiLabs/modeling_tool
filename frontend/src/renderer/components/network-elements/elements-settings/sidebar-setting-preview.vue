<template lang="pug">
.sidebar-setting-preview(v-if="havePreview")
  .preview-handler(@click="toggleSettingPreviewVisibility()")
    h4.sidebar-setting-preview-title Preview
    base-toggle-expand.primary(:value="isSettingPreviewVisible" :onClick="toggleSettingPreviewVisibility")      
  chart-switch.sidebar-data-settings_chart(
    v-show="isSettingPreviewVisible",
    :disable-header="true",
    :chart-data="storeCurrentElement.chartData",
    :chartIdx="currentEl.chartIdx",
    @chartIdxChange="handleChartIdxChange"
    class="sidebar-settings-preview-wrapper"
  )
</template>

<script>
import ChartSwitch from "@/components/charts/chart-switch.vue";
import { mapActions, mapGetters } from "vuex";
export default {
  name: "SidebarSettingPreview",
  inject: [],
  components: { ChartSwitch },
  props: {
    currentEl: { type: Object },
  },
  data() {
    return {
      previewValue: "",
      previewList: [],
      imgData: null,
      haveChartToDisplay: false,
    };
  },
  computed: {
    ...mapGetters({
      isTutorialMode: "mod_tutorials/getIsTutorialMode",
    }),
    layerId() {
      return this.currentEl.layerId;
    },
    storeCurrentElement() {
      return this.$store.getters["mod_workspace/GET_networkElementById"](
        this.layerId
      );
    },
    isSettingPreviewVisible() {
      return this.$store.state.mod_workspace.isSettingPreviewVisible;
    },
    havePreview() {
      return (
        this.storeCurrentElement.chartData &&
        this.storeCurrentElement.chartData.series &&
        this.storeCurrentElement.chartData.series[0].data !== ""
      );
    },
  },
  methods: {
    ...mapActions({
      api_getVariableList: "mod_api/API_getPreviewVariableList",
      api_getPreviewSample: "mod_api/API_getPreviewSample",
      api_getOutputDim: "mod_api/API_getOutputDim",
    }),
    toggleSettingPreviewVisibility() {
      this.$store.commit("mod_workspace/toggleSettingPreviewVisibility");
    },
    toSettings() {
      this.$emit("to-settings");
    },
    confirmSettings() {
      this.hideAllWindow();
    },
    getSample(variableName) {
      this.api_getPreviewSample({
        layerId: this.layerId,
        varData: variableName,
      }).then((data) => {
        this.previewValue = variableName;
        this.imgData = data;
        this.$store.dispatch("mod_workspace/SET_NetworkChartData", {
          layerId: this.layerId,
          payload: data,
        });
      });
    },
    haveData() {
      this.haveChartToDisplay =
        this.storeCurrentElement.chartData.series &&
        this.storeCurrentElement.chartData.series[0].data !== "";
    },
    handleChartIdxChange(chartIdx) {
      this.$store.dispatch("mod_workspace/SET_NetworkChartIdx", {
        layerId: this.layerId,
        payload: chartIdx,
      });
    },
  },
};
</script>
<style lang="scss" scoped>

  .preview-handler {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    border: $border-1;
    background: theme-var($neutral-7);
  }
  .sidebar-setting-preview-title {
    cursor: pointer;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 0;
  }

</style>
