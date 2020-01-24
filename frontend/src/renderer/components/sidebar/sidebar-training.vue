<template lang="pug">
  section.sidebar_content-padding--small
    sidebar-training-section(section-name="Progressbar")
      sidebar-progress(
        :progress-value="currentData.Progress"
      )
    sidebar-training-section(section-name="RAM")
      resource-monitor(
        monitor-value-key="Memory"
        :monitor-value="currentData"
      )
    sidebar-training-section(section-name="CPU")
      resource-monitor(
        monitor-value-key="GPU"
        :monitor-value="currentData"
      )
    sidebar-training-section(section-name="GPU")
      resource-monitor(
        monitor-value-key="GPU"
        :monitor-value="currentData"
      )

</template>

<script>
import SidebarProgress from "@/components/sidebar/sidebar-progress";
import SidebarTrainingSection from "@/components/sidebar/sidebar-training-section.vue";
import ResourceMonitor from "@/components/charts/resource-monitor.vue";

export default {
  name: "SidebarTraining",
  components: {SidebarProgress, ResourceMonitor, SidebarTrainingSection},
  data() {
    return {
      currentData: {
        Progress: 0,
        Memory: 0,
        CPU: 0
      },
      buffer: {}
    }
  },
  computed: {
    statusNetworkInfo() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus
    },
    doShowCharts() {
      return this.$store.getters['mod_workspace/GET_networkShowCharts']
    },
    isNeedWait() {
      return this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent']
    },
  },
  watch: {
    statusNetworkInfo(newVal) {
      this.isNeedWait
        ? this.buffer = newVal
        : this.currentData = newVal
    },
    doShowCharts() {
      this.isNeedWait
        ? this.currentData = this.buffer
        : null
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";

</style>
