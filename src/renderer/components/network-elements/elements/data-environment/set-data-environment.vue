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
            :chart-data="imgData"
        )

    template(slot="<i class='icon icon-search'></i> Unity-content")
      .settings-layer_section
        .form_row
          input.form_input(type="text" placeholder="c:" readonly
          v-model="inputPath"
          )
          button.btn.btn--primary(type="button"
            @click="loadFile"
            :disabled="disabledBtn"
          ) Load
        .form_row
          chart-switch.data-settings_chart(
            key="2"
            :disable-header="true"
            :chart-data="imgData"
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
            Path: [],
            Atari: 'Breakout', //select
            Category: 'Local',
            Type: 'Data',
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
        return `Action space: ${this.actionSpace}`
      }
    },
    watch: {
      'settings.accessProperties.Atari': {
        handler(newVal) {
          if(newVal) {
            this.dataSettingsPlot('DataEnvironment');
          }
        },
        immediate: true
      },
    },
    methods: {
      setTab(i) {
        this.tabSelected = i;
        this.settings.accessProperties.EnvType = this.tabs[i].type;
        this.imgData = null;
        this.dataSettingsPlot('DataEnvironment')
      },
      saveLoadFile(pathArr) {
        this.disabledBtn = false;
        this.settings.accessProperties.Path = pathArr;
        this.dataSettingsPlot('DataEnvironment')
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
          .then((pathArr)=> this.saveLoadFile(pathArr))
          .catch(()=> {
            this.disabledBtn = false;
          })
      }
    },
  }
</script>
