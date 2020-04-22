<template lang="pug">
  net-base-settings(
    :tab-set="tabs"
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row
          .form_label Distribution:
          .form_input
            base-radio(group-name="group1" value-input="Normal" v-model="settings.distribution")
              span Normal
            base-radio(group-name="group1" value-input="Uniform" v-model="settings.distribution")
              span Uniform
      .settings-layer_section(style="position:relative" v-if="settings.distribution=='Normal'")
        .form_row
          .form_label Mean:
          .form_input
            input(type="number" v-model="settings.mean")
      .settings-layer_section(style="position:relative" v-if="settings.distribution=='Normal'")
        .form_row
          .form_label Stddev:
          .form_input
            input(type="number" v-model="settings.stddev")
      .settings-layer_section(style="position:relative"  v-if="settings.distribution!='Normal'")
        .form_row
          .form_label Min:
          .form_input
            input(type="number" v-model="settings.min")
      .settings-layer_section(style="position:relative"  v-if="settings.distribution!='Normal'")
        .form_row
          .form_label Max:
          .form_input
            input(type="number" v-model="settings.max")
      .settings-layer_section(style="position:relative")
        .form_row
          .form_label Batch Size:
          .form_input
            input(type="number" v-model="settings.batch_size")
      .settings-layer_section
        .form_row
          .form_label Shape:
          .form_input
            input(type="string" v-model="settings.shape")

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
          mean: '0.1',
          stddev: '0.5',
          min: '0.1',
          batch_size: '3',
          max: '3.4',
          distribution: 'Normal',
          shape: '(1, 5, 7, 4, 7)',
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
