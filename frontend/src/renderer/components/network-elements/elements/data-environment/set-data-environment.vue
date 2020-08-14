<template lang="pug">
  div
    .settings-layer_section(style="position:relative")
      .form_row
        base-select(
          v-model="settings.accessProperties.Atari"
          :select-options="selectOptions"
          v-tooltip-interactive:right="interactiveInfo.selectGame"
        )
      .action_space(v-if="Mix_settingsData_actionSpace")
        span Action space:
        span {{Mix_settingsData_actionSpace}}

      set-data-environment-gym-img(
        :layer-settings="settings"
        :layer-id="currentEl.layerId"
        @apply-settings="applySettings"
      )
      //- .form_row
      //-   .form_label History length:
      //-   .form_input
      //-     input(type="number" v-model="settings.accessProperties.History_length")

    //-template(slot="<i class='icon icon-search'></i> Unity-content")
      .settings-layer_section
        .form_row
          input.form_input(type="text" placeholder="c:" readonly
          v-model="Mix_settingsData_inputPath"
          )
          button.btn.btn--primary(type="button"
            @click="loadFile"
            /:disabled="disabledBtn"
          ) Load
        .form_row
          chart-switch.data-settings_chart(
            key="2"
            /:disable-header="true"
            /:chart-data="imgData"
          )

</template>

<script>
  import mixinSet   from '@/core/mixins/net-element-settings.js';
  import mixinData  from '@/core/mixins/net-element-settings-data.js';

  import {openLoadDialog} from '@/core/helpers.js'

  import ChartSwitch from "@/components/charts/chart-switch.vue";
  import SetDataEnvironmentGymImg from "@/components/network-elements/elements/data-environment/set-data-environment--gym-img.vue";

  export default {
    name: 'SetDataEnvironment',
    mixins: [mixinSet, mixinData],
    components: {SetDataEnvironmentGymImg, ChartSwitch},
    // mounted() {
    //   this.getPreviewSample();
    // },
    mounted() {
      this.Mix_settingsData_getDataMeta(this.currentEl.layerId);
    },
    data() {
      return {
        //tabs: ['Gym', `<i class='icon icon-search'></i> Unity`],
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
             this.Mix_settingsData_getDataMeta(this.currentEl.layerId);
           }
         },
         //immediate: true
       },
     },
    methods: {
      // setTab(i) {
      //   this.tabSelected = i;
      //   console.log('setTab', i);
      //   if(i === 'Gym') this.getPreviewSample();
      //   // this.settings.accessProperties.EnvType = this.tabs[i].type;
      //   // this.Mix_settingsData_imgData = null;
      //   // this.Mix_settingsData_dataSettingsPlot('DataEnvironment')
      // },
      saveLoadFile(pathArr, type) {
        this.disabledBtn = false;
        // this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources(pathArr, type);
        // this.Mix_settingsData_dataSettingsPlot('DataEnvironment')
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
      },
      // getPreviewSample() {
      //   this.applySettings();
      //   this.$store.dispatch('mod_api/API_getPreviewSample', {layerId: this.currentEl.layerId, varData: 'sample'})
      //     .then((data)=> {
      //       this.imgData = data
      //     } )
      // }
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
