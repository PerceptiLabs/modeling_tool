<template lang="pug">
</template>

<script>
import mixinSet from "@/core/mixins/net-element-settings.js";
import { deepCopy } from "@/core/helpers.js";
export default {
  name: "SetLayerCustom",
  mixins: [mixinSet],
  mounted() {
    if (!this.currentEl.layerCode) {
      const saveSettings = {
        elId: this.currentEl.layerId,
        code: { Output: null },
        set: null,
        tabName: "Code"
      };
      this.$store.dispatch("mod_workspace/SET_elementSettings", {
        settings: deepCopy(saveSettings)
      });
    }
  },
  data() {
    return {
      tabs: ["Code"]
    };
  }
};
</script>
