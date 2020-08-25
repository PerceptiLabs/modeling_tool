<template lang="pug">
  perfect-scrollbar.information-panel-content(
    ref="log-items")
    div(
      v-for="l in kernelLogs"
      :key="l.id") 
      .log-item {{ l.message }}
</template>

<script>
export default {
  name: "ConsoleInfoPanel",
  computed: {
    kernelLogs() {
      const currentNetworkId = this.$store.getters['mod_workspace/GET_currentNetworkId'];

      return this.$store.getters['mod_logs/getKernelLogs'](currentNetworkId);
    }
  },
  watch: {
    kernelLogs(newVal) {
      this.$nextTick(() => {
        if (!this.$refs['log-items']) { return; }

        this.$refs['log-items'].$el.scrollTop = this.$refs['log-items'].$el.scrollHeight;
      });      
    }
  }
}
</script>

<style lang="scss" scoped>

  $information-panel-font-size: 1.2rem;
  .information-panel-content {
    padding: 0 1rem;
    height: 100%;
    overflow-y: auto;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: $information-panel-font-size;
    line-height: 1.2rem;
  }

  .log-item {
    padding: 0.5rem 0;
  }
</style>