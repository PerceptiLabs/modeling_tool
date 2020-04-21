<template lang="pug">
  net-base-settings(
    :tab-set="tabs"
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section(style="position:relative")
        .form_row
          .form_label Mean:
          .form_input
            input(type="number" v-model="settings.mean")

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
  import mixinSet   from '@/core/mixins/net-element-settings.js';
  import mixinData  from '@/core/mixins/net-element-settings-data.js';
  
  export default {
    name: 'SetDataRandom',
    mixins: [mixinSet, mixinData],
    mounted() {
      this.Mix_settingsData_getDataMeta(this.currentEl.layerId);
    },
    data() {
      return {
        tabs: ['Settings', 'Code'],
        settings: {
          mean: '0.1'
        },
      }
    },
  }
</script>


<style scoped lang="scss">
  @import "../../../../scss/base";
  .action_space {
    position: relative;
    background: $col-txt2;
    top: 24px;
    padding: 4px 10px;
    display: flex;
    justify-content: space-between;
  }
</style>
