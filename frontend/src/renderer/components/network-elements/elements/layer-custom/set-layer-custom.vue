<template lang="pug">
  net-base-settings(
    :tab-set="tabs"
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet     from '@/core/mixins/net-element-settings.js';
import { deepCopy } from "@/core/helpers.js";
export default {
  name: 'SetLayerCustom',
  mixins: [mixinSet],
  mounted() {
    if(!this.currentEl.layerCode) {
      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': {Output: null},
        'set': null,
        'tabName': 'Code'
      };
      this.$store.dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings));
    }
  },
  data() {
    return {
      tabs: ['Code'],
    }
  }
}
</script>
