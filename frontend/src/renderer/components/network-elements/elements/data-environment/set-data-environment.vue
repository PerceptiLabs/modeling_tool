<template lang="pug">
  div
    .settings-layer_section(style="position:relative")
      .form_row.flex-column.align-items-start
        .form_label Environment
        base-select(
          v-model="settings.accessProperties.Atari"
          :select-options="selectOptions"
          v-tooltip-interactive:right="interactiveInfo.selectGame"
        )
      .action_space(v-if="Mix_settingsData_actionSpace")
        span Action space:
        span {{Mix_settingsData_actionSpace}}

</template>

<script>
  import mixinSet   from '@/core/mixins/net-element-settings.js';
  import mixinData  from '@/core/mixins/net-element-settings-data.js';
  import ChartSwitch from "@/components/charts/chart-switch.vue";
  import SetDataEnvironmentGymImg from "@/components/network-elements/elements/data-environment/set-data-environment--gym-img.vue";

  export default {
    name: 'SetDataEnvironment',
    mixins: [mixinSet, mixinData],
    components: {SetDataEnvironmentGymImg, ChartSwitch},
    mounted() {
      this.Mix_settingsData_getDataMeta(this.currentEl.layerId).then(() => {
        this.saveSettingsToStore("Settings");
      });
    },
    data() {
      return {
        tabs: ['Gym', 'Code'],
        disabledBtn: false,
        imgData: null,
        selectOptions: [
          { text: 'Breakout',     value: 'Breakout' },
          { text: 'BankHeist',    value: 'BankHeist' },
          { text: 'DemonAttack',  value: 'DemonAttack' }
        ],

        settings: {
          Type: 'Environment',
          accessProperties: {
            EnvType: 'Gym',
            //Path: [],
            Sources: [], //{type: 'file'/'directory', path: 'PATH'}
            Atari: 'Breakout', //select
            Category: 'Local',
            Type: 'Data',
            // History_length: 10,
          }
        },
        interactiveInfo: {
          selectGame: {
            title: 'Select',
            text: 'Choose game environment'
          },
        }
      }
    },
    computed: {
      chartLabel() {
        return `Action space: ${this.Mix_settingsData_actionSpace}`
      }
    },
     watch: {
       'settings.accessProperties.Atari': {
         handler(newVal) {
          if(newVal) {
            this.Mix_settingsData_getDataMeta(this.currentEl.layerId).then(() => {
              this.saveSettingsToStore("Settings");
            });
          }
         },
       },
     },
    methods: {
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
    margin-bottom: 30px;
  }
</style>
