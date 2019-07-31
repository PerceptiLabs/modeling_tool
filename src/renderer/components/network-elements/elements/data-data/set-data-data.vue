<template lang="pug">
  net-base-settings(
    :tab-set="tabs"
    :current-el="currentEl"
  )
    template(slot="Computer-content")
      .settings-layer_section.section-data-select(v-if="!settings.accessProperties.Path.length")
        button.btn.tutorial-relative(type="button"
          @click="loadFolder"
          v-tooltip-interactive:bottom="interactiveInfo.folder"
        )
          i.icon.icon-open-folder
        span.data-select_text or
        button.btn.tutorial-relative(type="button"
          @click="loadFile"
          id="tutorial_button-load"
          v-tooltip-interactive:right="interactiveInfo.file"
        )
          i.icon.icon-open-file
      .settings-layer_section(v-else)
        .form_row
          button.btn.btn--link(type="button" @click="clearPath")
            i.icon.icon-backward
            span Back
        .form_row
          input.form_input(type="text" v-model="inputPath" readonly="readonly")
        .form_row(v-if="dataColumns.length")
          base-select(
            v-model="dataColumnsSelected"
            :select-options="dataColumns"
            :select-multiple="true"
          )
        .form_row
          chart-switch.data-settings_chart(
            :disable-header="true"
            :chart-data="imgData"
          )

    template(slot="Cloud-content")
      //-settings-cloud

    template(slot="Computer-action")
      button.btn.btn--primary.tutorial-relative(type="button"
        v-show="settings.accessProperties.Path.length"
        @click="saveSettings('Computer')"
        id="tutorial_button-apply"
      ) Apply
    template(slot="Cloud-action")
      span

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import mixinData      from '@/core/mixins/net-element-settings-data.js';

  import SettingsCloud  from '@/components/network-elements/elements-settings/setting-clouds.vue';
  import ChartSwitch    from "@/components/charts/chart-switch.vue";

  import {openLoadDialog, loadPathFolder} from '@/core/helpers.js'
  import {mapActions, mapGetters}     from 'vuex';

  export default {
    name: 'SetDataData',
    mixins: [mixinSet, mixinData],
    components: {ChartSwitch, SettingsCloud },
    mounted() {
      if(this.settings.accessProperties.Columns.length) {
        this.dataColumnsSelected = this.settings.accessProperties.Columns;
      }
      this.getDataMeta('DataData')
        .then((data)=> {
          if (data.Columns.length) this.createSelectArr(data.Columns);
          this.getDataPlot('DataData');
        })
    },
    data() {
      return {
        //tabs: ['Computer', 'Cloud'],
        tabs: ['Computer'],
        dataColumns: [],
        dataColumnsSelected: [],
        interactiveInfo: {
          folder: {
            title: 'Select Folder',
            text: 'Select a folder where the data is stored'
          },
          file: {
            title: 'Select File',
            text: 'Select a file that is the data'
          }
        },
        settings: {
          Type: 'Data',
          accessProperties: {
            Columns: [],
            Dataset_size: 3000,
            Category:'Local',
            Type: 'Data',
            Path: [],
          }
        }
      }
    },
    computed: {
      ...mapGetters({
        appPath:        'globalView/GET_appPath',
        isTutorialMode: 'mod_tutorials/getIstutorialMode',
      })
    },
    watch: {
      dataColumnsSelected(newVal) {
        this.settings.accessProperties.Columns = newVal;
        this.getDataPlot('DataData')
      },

    },
    methods: {
      ...mapActions({
        tutorialPointActivate: 'mod_tutorials/pointActivate',
      }),
      loadFile() {
        let optionBasic = {
          title:"Load file or files",
          properties: ['openFile', 'multiSelections'],
          filters: [
            {name: 'All', extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'txt', 'json', 'csv', 'mat', 'npy', 'npz']},
            {name: 'Images', extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff']},
            {name: 'Text', extensions: ['txt', 'json', 'csv', 'mat', 'npy', 'npz']},
          ]
        };
        let optionTutorial = {
          title:"Load file",
          defaultPath: `${this.appPath}basic-data`,
          properties: ['openFile'],
          filters: [
            {name: 'All', extensions: ['npy']},
          ]
        };
        let optionDialog = this.isTutorialMode ? optionTutorial : optionBasic;
        openLoadDialog(optionDialog)
          .then((pathArr)=> this.saveLoadFile(pathArr))
          .catch(()=> {
          })
      },
      loadFolder() {
        loadPathFolder()
          .then((pathArr)=> this.saveLoadFile(pathArr))
          .catch(()=> {
          })
      },
      saveLoadFile(pathArr) {
        this.settings.accessProperties.Path = pathArr;
        this.getSettingsInfo();
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-load'})
      },
      clearPath() {
        this.deleteDataMeta('DataData')
          .then(()=> {
            this.settings.accessProperties.Path = [];
            this.getSettingsInfo()
          })
          .catch(()=> console.log('set-data-data 144 err'))
      },
      getSettingsInfo() {
        if(this.settings.accessProperties.Path.length) {
          this.dataSettingsMeta('DataData')
            .then((data)=>{
              if (data.Columns.length) {
                this.createSelectArr(data.Columns);
                return data
              }
            })
            .then(()=> this.getDataPlot('DataData'))
        }
      },
      createSelectArr(data) {
        data.forEach((el, index) => this.dataColumns.push({text: el, value: index}));
        this.dataColumnsSelected.push(this.dataColumns[0].value);
      },
      saveSettings(tabName) {
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-apply'})
        this.applySettings(tabName);
        this.confirmSettings();
      }
    }
  }
</script>
<style lang="scss" scoped>
  @import "../../../../scss/base";
  .settings-layer {
    justify-content: center;
  }
  .section-data-select {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    padding-bottom: 0;
    .btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 6.4rem;
      height: 6.4rem;
      background-color: $bg-input;
      font-size: 4rem;
      &:hover {
        box-shadow: inset 0 0 1px 1px $color-5;
      }
    }
  }
  .data-select_text {
    margin: 0 1.4rem;
  }
</style>