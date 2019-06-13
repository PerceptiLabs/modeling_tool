<template lang="pug">
  net-base-settings(:tab-set="tabs")
    template(slot="Computer-content")
      .settings-layer_section.section-data-select(v-if="!settings.accessProperties.Path.length")
        button.btn.tutorial-relative(type="button"
          :disabled="disabledBtn"
          @click="loadFolder"
          v-tooltip-interactive:bottom="interactiveInfo.folder"
        )
          i.icon.icon-open-folder
        span.data-select_text or
        button.btn.tutorial-relative(type="button"
          :disabled="disabledBtn"
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
        request-spinner(:showSpinner="showRequestSpinner")
          chart-switch.data-charts(
            :disable-header="true"
            :chart-data="imgData"
          )

    template(slot="Cloud-content")
      settings-cloud

    template(slot="action")
      button.btn.btn--primary.tutorial-relative(type="button"
        v-show="settings.accessProperties.Path.length"
        @click="saveSettings"
        id="tutorial_button-apply"
      ) Apply

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import mixinData      from '@/core/mixins/net-element-settings-data.js';

  import SettingsCloud  from '@/components/network-elements/elements-settings/setting-clouds.vue';
  import ChartSwitch    from "@/components/charts/chart-switch.vue";

  import {openLoadDialog, loadPathFolder} from '@/core/helpers.js'
  //import coreRequest      from "@/core/apiCore.js";
  import {mapActions}     from 'vuex';
  import RequestSpinner from '@/components/different/request-spinner.vue'

  export default {
    name: 'SetDataData',
    mixins: [mixinSet, mixinData],
    components: {ChartSwitch, SettingsCloud, RequestSpinner },
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
        tabs: ['Computer', 'Cloud'],
        dataColumns: [],
        dataColumnsSelected: [],
        disabledBtn: false,
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
        },
        showRequestSpinner: true
      }
    },
    watch: {
      dataColumnsSelected(newVal) {
        this.settings.accessProperties.Columns = newVal;
        this.getDataPlot('DataData')
      },
      imgData(newVal, oldVal) {
        if(newVal !== oldVal) this.showRequestSpinner = false;
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate: 'mod_tutorials/pointActivate',
      }),
      openLoadDialog,
      loadPathFolder,
      loadFile() {
        this.disabledBtn = true;
        let opt = {
          title:"Load file or files",
          properties: ['openFile', 'multiSelections'],
          filters: [
            {name: 'All', extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'txt', 'json', 'csv', 'mat', 'npy', 'npz']},
            {name: 'Images', extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff']},
            {name: 'Text', extensions: ['txt', 'json', 'csv', 'mat', 'npy', 'npz']},
          ]
        };
        this.openLoadDialog(opt)
          .then((pathArr)=> this.saveLoadFile(pathArr))
          .catch(()=> {
            this.disabledBtn = false;
          })
      },
      loadFolder() {
        this.disabledBtn = true;
        this.loadPathFolder()
          .then((pathArr)=> this.saveLoadFile(pathArr))
          .catch(()=> {
            this.disabledBtn = false;
          })
      },
      saveLoadFile(pathArr) {
        this.disabledBtn = false;
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
      saveSettings() {
        this.applySettings();
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-apply'})
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