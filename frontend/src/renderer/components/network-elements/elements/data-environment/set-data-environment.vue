<template lang="pug">
  div
    .settings-layer_section(style="position:relative")
      .form_row.flex-column.align-items-start
        .form_label Choose engine
        base-select(
          v-model="settings.accessProperties.EnvType"
          :select-options="envOptions"
        )
      .line-break &nbsp;
      .form_row.flex-column.align-items-start(v-if="settings.accessProperties.EnvType === 'Gym'")
        .form_label Environment
        base-select(
          v-model="settings.accessProperties.Atari"
          :select-options="atariSelectOptions"
          v-tooltip-interactive:right="interactiveInfo.selectGame"
        )
      .action_space(v-if="Mix_settingsData_actionSpace && settings.accessProperties.EnvType === 'Gym'")
        span Action space:
        span {{Mix_settingsData_actionSpace}}
  
      div(v-if="settings.accessProperties.EnvType === 'Unity'")
        .form_row.flex-column.align-items-start
          .form_label.label-margin Environment
          base-select(
            v-model="settings.accessProperties.unity_env_enviroment"
            :select-options="unityEnviromentSelectOption")
        div.spacer
        .form_label.label-margin Choose the .yaml file for your environment
        input.form_input(
          type="text"
          v-model="settings.accessProperties.unity_env_path"
          @focus="setIsSettingInputFocused(true)"
          @blur="setIsSettingInputFocused(false)")
        div.settings-layer_section.d-flex.justify-content-center
          button.btn.btn-open-popup.tutorial-relative(type="button"
          @click="openFilePicker('file')"
            )
              i.icon.icon-open-file
              span Load data
      
        div(v-if="showFilePicker")  
          file-picker-popup(
            :filePickerType="filePickerType"
            :fileTypeFilter="validFileExtensions"
            :confirmCallback="confirmFilePickerSelection"
            :cancelCallback="clearPath"
            :options="{showToTutotialDataFolder: false}"
            )
      //- set-data-environment-gym-img(
      //-   :layer-settings="settings"
      //-   :layer-id="currentEl.layerId"
      //-   @apply-settings="applySettings"
      //- )
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
  import ChartSwitch from "@/components/charts/chart-switch.vue";
  import SetDataEnvironmentGymImg from "@/components/network-elements/elements/data-environment/set-data-environment--gym-img.vue";
  import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';

  export default {
    name: 'SetDataEnvironment',
    mixins: [mixinSet, mixinData, mixinFocus],
    components: {SetDataEnvironmentGymImg, ChartSwitch, FilePickerPopup},
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
        atariSelectOptions: [
          { text: 'Breakout',     value: 'Breakout' },
          { text: 'BankHeist',    value: 'BankHeist' },
          { text: 'DemonAttack',  value: 'DemonAttack' }
        ],
        unityEnviromentSelectOption: [
          'Basic',
          '3DBall',
          '3DBallHard',
          'GridWorld',
          'Hallway',
          'VisualHallway',
          'CrawlerDynamicTarget',
          'CrawlerStaticTarget',
          'Bouncer',
          'SoccerTwos',
          'PushBlock',
          'VisualPushBlock',
          'WallJump',
          'Tennis',
          'Reacher',
          'Pyramids',
          'VisualPyramids',
          'Walker',
          'FoodCollector',
          'VisualFoodCollector',
          'StrikersVsGoalie',
          'WormStaticTarget',
          'WormDynamicTarget',
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
            unity_env_path: '',
            unity_env_enviroment: '',
            // History_length: 10,
          },
        },
        envOptions: [
          { text: 'Gym', value: 'Gym'},
          { text: 'Unity', value: 'Unity'},
        ],
        interactiveInfo: {
          selectGame: {
            title: 'Select',
            text: 'Choose game environment'
          },
        },
        filePickerType: 'file',
        showFilePicker: false,
        
      }
    },
    computed: {
      chartLabel() {
        return `Action space: ${this.Mix_settingsData_actionSpace}`
      },
      validFileExtensions() {
        let optionBasic = ['yaml'];
        return optionBasic;
      }
    },
     watch: {
       "settings.accessProperties": {
         deep: true,
         handler() {
           this.saveSettingsToStore("Settings");
         }
       },
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
      openFilePicker(fileType) {
        this.showFilePicker = true;
        this.filePickerType = fileType;
      },
      confirmFilePickerSelection(path) {
        this.showFilePicker = false;
        this.settings.accessProperties.unity_env_path = path[0];
      },
      clearPath(){
        this.showFilePicker = false;
      },
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
  .use-unity-checkbox {
    width: 100%;
  }
  .btn-open-popup {
      display: inline-flex;
      align-items: center;
      width: 15.5rem;
      height: 3.4rem;
      padding: 0 1.5rem;
      background: rgba(97, 133, 238, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 2px;

      font-family: Nunito Sans;
      font-style: normal;
      font-weight: 600;
      font-size: 1.2rem;

      font-weight: 300;
      + .btn {
        margin-top: .8rem;
      }
      .icon {
        font-size: 1.75rem;
        margin-right: 0.5rem;
      }
      &:hover {
        box-shadow: inset 0 0 1px 1px $color-5;
      }
    }
   
    .spacer {
      margin: 10px 0;
    }
    .line-break {
      margin: 15px -10px 0 -10px;
      border-top: 1px solid #343948;
    }
    .label-margin {
      margin-top: .5rem;
      margin-bottom: .5rem;
    }
</style>

