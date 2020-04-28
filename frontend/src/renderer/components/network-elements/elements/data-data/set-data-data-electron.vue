<template lang="pug">
  net-base-settings(
    :tab-set="dynamicTabs"
    :current-el="currentEl"
    id-set-btn="tutorial_button-apply"
    @press-apply="saveSettings($event)"
  )
    template(slot="Computer-content")
      .settings-layer_section.section-data-select(v-if="!settings.accessProperties.Sources.length")

        button.btn.tutorial-relative(type="button"
          @click="loadFile"
          id="tutorial_button-load"
          v-tooltip-interactive:right="interactiveInfo.file"
        )
          i.icon.icon-open-file
          span Choose files

        button.btn.tutorial-relative(type="button"
          @click="loadFolder"
          v-tooltip-interactive:bottom="interactiveInfo.folder"
        )
          i.icon.icon-open-folder
          span Choose folders

      template(v-else)
        //-chart-spinner(v-if="showSpinner")
        .settings-layer_section
          .form_row
            button.btn.btn--link(type="button" @click="clearPath")
              i.icon.icon-backward
              span Back
        .settings-layer_section.settings-layer_section--data
          .form_row
            settings-file-list(
              v-model="fileList"
              :name-add-item="typeOpened"
              :show-spinner="showSpinner"
              @partition-list="setPartitionList"
              @add-file="addFiles"
            )
            //
          .form_row(v-if="settings.accessProperties.Sources.length > 1")
            .form_label Summary:
            .form_input
              triple-input.file-list-item_settings(
                v-model="Mix_settingsData_Partition_summary"
                :disable-edit="true"
                separate-sign="%"
              )
        .settings-layer_section.settings-layer_section--data
          //- .form_row
          //-   .form_label Batch size:
          //-   .form_input
          //-     input(type="number" v-model="settings.accessProperties.Batch_size")
          .form_row
            base-checkbox.bigest-text(v-model="settings.accessProperties.Shuffle_data") Shuffle
        .settings-layer_section
          .form_row(v-if="dataColumns.length")
            base-select(
              v-model="dataColumnsSelected"
              :select-options="dataColumns"
              :select-multiple="true"
            )
        //-.settings-layer_foot
          button.btn.btn--primary(type="button") Apply
    //-template(slot="Cloud-content")
      //-settings-cloud
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )
    template(slot="Computer-action")

    //-template(slot="Cloud-action")
      span
    template(slot="Code-action")


</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import mixinData      from '@/core/mixins/net-element-settings-data.js';

  import SettingsCloud  from '@/components/network-elements/elements-settings/setting-clouds.vue';
  import SettingsFileList  from '@/components/network-elements/elements-settings/setting-file-list.vue';
  import ChartSwitch    from "@/components/charts/chart-switch.vue";
  import TripleInput    from "@/components/base/triple-input";
  import ChartSpinner   from '@/components/charts/chart-spinner'

  import {openLoadDialog, loadPathFolder} from '@/core/helpers.js'
  import {mapActions, mapGetters}     from 'vuex';

  export default {
    name: 'SetDataData',
    mixins: [mixinSet, mixinData],
    components: {ChartSwitch, SettingsCloud, TripleInput, SettingsFileList, ChartSpinner },
    mounted() {
      if(this.settings.accessProperties.Columns.length) {
        this.dataColumnsSelected = this.settings.accessProperties.Columns;
      }
    },
    data() {
      return {
        //tabs: ['Computer', 'Cloud'],
        tabs: ['Computer', 'Code'],
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
            //Path: [],
            Sources: [], //{type: 'file'/'directory', path: 'PATH'}
            Partition_list: [],
            // Batch_size: 10,
            Shuffle_data: true,
          }
        },
        showSpinner: false
      }
    },
    computed: {
      ...mapGetters({
        appPath:        'globalView/GET_appPath',
        isTutorialMode: 'mod_tutorials/getIstutorialMode',
      }),
      dynamicTabs() {
        return this.settings.accessProperties.Sources.length ? ['Computer', 'Code'] : ['Computer']
      },
      typeOpened() {
        const path = this.settings.accessProperties.Sources;
        if(path.length) return path[0].type;
        else return ''
      },
      fileList: {
        get() {
          const path = this.settings.accessProperties.Sources;
          const partitionList = this.settings.accessProperties.Partition_list;
          const fileArray = path.map((item, index)=> {
            return {
              path: item.path,
              type: item.type,
              settings: partitionList[index] || [70, 20, 10]
            };
          });
          const partList = fileArray.map((item)=> item.settings);
          this.settings.accessProperties.Partition_list = partList;
          return fileArray;
        },
        set(newVal) {
          const partitionList = newVal.map((item)=> item.settings);
          const pathList =      newVal.map((item)=> {
            return {
              path: item.path,
              type: item.type
            }});
          this.settings.accessProperties.Sources = pathList;
          this.settings.accessProperties.Partition_list = partitionList;
        }
      }
    },
    watch: {
      dataColumnsSelected(newVal) {
        this.settings.accessProperties.Columns = newVal;
        //this.Mix_settingsData_getDataPlot('DataData')
        //this.Mix_settingsData_getPreviewVariableList(this.currentEl.layerId)
      },
      fileList: {
        handler(newVal) {
          this.Mix_settingsData_getPartitionSummary(this.currentEl.layerId);
        },
        deep: true,
        //immediate: true
      },
      'settings.accessProperties.Sources.length': {
        handler(newVal) {
          if(newVal) this.$nextTick(()=> { this.showBtn() });
          else this.$nextTick(()=> { this.hideBtn() });
          this.getSettingsInfo()
        },
        immediate: true
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:  'mod_tutorials/pointActivate',
        // API_getPartitionSummary:'mod_api/API_getPartitionSummary',
        // API_getDataMeta:        'mod_api/API_getDataMeta',
      }),
      setPartitionList(list) {
        this.settings.accessProperties.Partition_list = list
      },
      loadFile(isAppend) {
        let optionBasic = {
          title:"Load file or files",
          properties: ['openFile', 'multiSelections'],
          filters: [
            {name: 'All',     extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'txt', 'json', 'csv', 'mat', 'npy', 'npz']},
            {name: 'Images',  extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff']},
            {name: 'Text',    extensions: ['txt', 'json', 'csv', 'mat', 'npy', 'npz']},
          ]
        };
        let optionTutorial = {
          title: "Load file",
          buttonLabel: 'Load file',
          defaultPath: `${this.appPath}basic-data`,
          properties: ['openFile'],
          filters: [
            {name: 'All', extensions: ['npy']},
          ]
        };
        let optionDialog = this.isTutorialMode ? optionTutorial : optionBasic;
        openLoadDialog(optionDialog)
          .then((pathArr)=> this.saveLoadFile(pathArr, 'file', isAppend))
          .catch(()=> { })
      },
      loadFolder(isAppend) {
        loadPathFolder()
          .then((pathArr)=> this.saveLoadFile(pathArr, 'directory', isAppend))
          .catch(()=> { })
      },
      addFiles() {
        if(this.typeOpened === 'file') this.loadFile(true);
        else this.loadFolder(true)
      },
      saveLoadFile(pathArr, type, isAppend) {
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-load'});
        if(isAppend) {
          const allPath = [... this.settings.accessProperties.Sources.map((el)=> el.path), ...pathArr];
          this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources([... new Set(allPath)], type)
        }
        else this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources(pathArr, type);
        //this.getSettingsInfo();
      },
      clearPath() {
        this.Mix_settingsData_deleteDataMeta('DataData')
          .then(()=> {
            this.settings.accessProperties.Sources = [];
            //this.getSettingsInfo()
          })
          .catch((err)=> console.log(err))
      },
      getSettingsInfo() {
        if(this.settings.accessProperties.Sources.length) {

          this.Mix_settingsData_getDataMeta(this.currentEl.layerId)
            .then((data) => {
              //console.log(data);
              if (data.Columns && data.Columns.length) this.createSelectArr(data.Columns);
            });

        }
      },
      createSelectArr(data) {
        let selectArr = [];
        data.forEach((el, index)=> selectArr.push({text: el, value: index}));
        this.dataColumns = [...selectArr];
        this.dataColumnsSelected.push(this.dataColumns[0].value);
      },
      saveSettings(tabName) {
        this.applySettings(tabName);
        this.checkPartitionList();
        this.$nextTick(()=> this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-apply'}))
      },
      checkPartitionList() {
        this.settings.accessProperties.Partition_list.forEach((item)=> {
          if(item[0]+item[1]+item[2] !== 100) {
            this.$store.dispatch('globalView/GP_errorPopup', `Train + Validate + Test must be 100%`)
          }
        })
      },
      hideBtn() {
        const btn = document.getElementById('js-hide-btn');
        if(btn) btn.style.cssText = 'display: none'
      },
      showBtn() {
        const btn = document.getElementById('js-hide-btn');
        if(btn) btn.style.cssText = ''
      },
    }
  }
</script>
<style lang="scss">
  @import "../../../../scss/base";
  .settings-layer_section.settings-layer_section--data {
    input {
      background-color: #6E778C;
    }
  }
  .section-data-select {
    /*display: flex;*/
    /*align-items: center;*/
    /*justify-content: center;*/
    font-size: 1.4rem;
    text-align: center;

    .btn {
      display: inline-flex;
      align-items: center;
      width: 15.5rem;
      height: 3.4rem;
      padding: 0 1.5rem;
      background-color: $bg-input;
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
  }
  .data-select_text {
    margin: 0 1.4rem;
  }
  .settings-layer_section .file-list-item_settings {
    font-size: 1rem;
    .triple-input_input {
      max-width: 2.8em;
    }
    .triple-input_input ~ .triple-input_input {
      margin-left: 1em;
    }
  }
  .settings-layer_section--data label.bigest-text {
    font-size: 1.4rem
  }
</style>
