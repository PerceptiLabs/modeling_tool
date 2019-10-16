<template lang="pug">
  net-base-settings(
    :tab-set="tabs"
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Gym-content")
      .settings-layer_section(style="position:relative")
        .form_row
          base-select(
            v-model="settings.accessProperties.Atari"
            :select-options="selectOptions"
            v-tooltip-interactive:right="interactiveInfo.selectGame"
          )
        .form_row(v-tooltip-interactive:right="interactiveInfo.actionSpace")
          chart-switch(
            key="1"
            :chart-label="chartLabel"
            :chart-data="Mix_settingsData_imgData"
          )
        .form_row
          .form_label Batch size:
          .form_input
            input(type="number" v-model="settings.accessProperties.Batch_size")

    template(slot="<i class='icon icon-search'></i> Unity-content")
      .settings-layer_section
        .form_row
          input.form_input(type="text" placeholder="c:" readonly
          v-model="Mix_settingsData_inputPath"
          )
          button.btn.btn--primary(type="button"
            @click="loadFile"
            :disabled="disabledBtn"
          ) Load
        .form_row
          chart-switch.data-settings_chart(
            key="2"
            :disable-header="true"
            :chart-data="Mix_settingsData_imgData"
          )

</template>

<script>
  import mixinSet   from '@/core/mixins/net-element-settings.js';
  import mixinData  from '@/core/mixins/net-element-settings-data.js';

  import {openLoadDialog} from '@/core/helpers.js'

  import ChartSwitch from "@/components/charts/chart-switch.vue";

  export default {
    name: 'SetDataEnvironment',
    mixins: [mixinSet, mixinData],
    components: { ChartSwitch},
    data() {
      return {
        tabs: ['Gym', `<i class='icon icon-search'></i> Unity`],
        disabledBtn: false,
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
            Batch_size: 10,
          }
        },
        interactiveInfo: {
          selectGame: {
            title: 'Select',
            text: 'Choose game environment'
          },
          actionSpace: {
            title: 'Action Space',
            text: 'Number of different actions </br> you can take in the game'
          }
        }
      }
    },
    computed: {
      chartLabel() {
        return `Action space: ${this.Mix_settingsData_actionSpace}`
      }
    },
    watch: {
      // 'settings.accessProperties.Atari': {
      //   handler(newVal) {
      //     if(newVal) {
      //       this.Mix_settingsData_getDataPlot('DataEnvironment');
      //     }
      //   },
      //   immediate: true
      // },
    },
    methods: {
      setTab(i) {
        this.tabSelected = i;
        this.settings.accessProperties.EnvType = this.tabs[i].type;
        this.Mix_settingsData_imgData = null;
        this.Mix_settingsData_dataSettingsPlot('DataEnvironment')
      },
      saveLoadFile(pathArr, type) {
        this.disabledBtn = false;
        this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources(pathArr, type);
        this.Mix_settingsData_dataSettingsPlot('DataEnvironment')
      },
      loadFile() {
        this.disabledBtn = true;
        let opt = {
          title:"Load file or files",
          properties: ['openFile', 'multiSelections'],
          filters: [
            {name: 'All', extensions: ['exe']},
          ]
        };
        openLoadDialog(opt)
          .then((pathArr)=> this.saveLoadFile(pathArr, 'file'))
          .catch(()=> {
            this.disabledBtn = false;
          })
      }
    },
  }
</script>
