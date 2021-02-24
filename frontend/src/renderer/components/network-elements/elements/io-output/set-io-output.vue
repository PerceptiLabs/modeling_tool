<template lang="pug">
  div
    .settings-layer_section.section-data-select(v-if="!settings.accessProperties.Sources.length && !showFilePicker" id="tutorial_button-load")
      button.btn.tutorial-relative(type="button"
        @click="openFilePicker('multimode')"
        v-if="!showFilePicker"
        )
          i.icon.icon-open-file
          span Load CSV data

    template(v-else-if="showFilePicker")
      file-picker-popup(
        :filePickerType="filePickerType"
        :fileTypeFilter="validFileExtensions"
        :confirmCallback="confirmFilePickerSelection"
        :cancelCallback="closeFilePicker"
        :options="{showToTutotialDataFolder: true}"
        )

    template(v-else)
      .settings-layer_section
        .form_row
          button.btn.btn--link(type="button" @click="clearPath")
            img(src="../../../../../../static/img/back.svg")
        .form_row.flex-column.align-items-start(v-if="dataColumns.length")
          .form_label Columns
          base-select(
            v-model="dataColumnsSelected"
            :select-options="dataColumns"
            :select-multiple="true"
          )
      .settings-layer_section.settings-layer_section--data
        .form_row
          settings-file-list(
            v-model="fileList"
            :name-add-item="typeOpened"
            @partition-list="setPartitionList"
            @add-file="addFiles"
            @handle-focus="setIsSettingInputFocused(true)"
            @handle-blur="setIsSettingInputFocused(false)"
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
        .form_row
          base-checkbox.light-text(v-model="settings.accessProperties.Shuffle_data") Shuffle

      .settings-layer_section
          .form_row
            .form_label Feature name:
            .form_input
              input.w-full(
                type="text"
                v-model="settings.FeatureName"
                @focus="setIsSettingInputFocused(true)"
                @blur="setIsSettingInputFocused(false)")



</template>

<script>
  import mixinSet         from '@/core/mixins/net-element-settings.js';
  import mixinData        from '@/core/mixins/net-element-settings-data.js';
  import mixinFocus       from '@/core/mixins/net-element-settings-input-focus.js';

  import SettingsCloud    from '@/components/network-elements/elements-settings/setting-clouds.vue';
  import SettingsFileList from '@/components/network-elements/elements-settings/setting-file-list.vue';
  import ChartSwitch      from "@/components/charts/chart-switch.vue";
  import TripleInput      from "@/components/base/triple-input";
  import WebUploadFile    from "@/components/web/upload-file.vue";
  import FilePicker       from "@/components/different/file-picker.vue";
  import FilePickerPopup  from "@/components/global-popups/file-picker-popup.vue";

  import { debounce }     from '@/core/helpers.js'
  import { mapGetters }   from 'vuex';

  export default {
    name: 'SetIoOutput',
    mixins: [mixinSet, mixinData, mixinFocus],
    components: {ChartSwitch, SettingsCloud, TripleInput, SettingsFileList, WebUploadFile, FilePicker, FilePickerPopup },
    mounted() {
      if (this.settings.FilePath && this.settings.accessProperties.Sources.length === 0) {
        this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources([this.settings.FilePath], 'file');
        this.settings.accessProperties.Partition_list = [[70, 20, 10]];
      }
      this.debouncedSaveSettingsFunction = debounce((tabName, pushOntoHistory) => {
        this.applySettings(tabName, pushOntoHistory);
      }, 500);

      this.saveSettingsToStore("Computer");
    },
    data() {
      return {
        tabs: ['Computer', 'Code'],
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
        testPath: [''],
        testSelectFile: true,
        settings: {
          Type: 'IoOutput',
          FeatureName: '',
          FilePath: '',
          DataType: '',
          testInfoIsInput: true,//input  false - labels
          accessProperties: {
            Sources: [], //{type: 'file'/'directory', path: 'PATH'}
          }
        },
        showFilePicker: false,
        filePickerType: 'file', // or 'folder', 'multimode'
        filePickerAppendingItems: false,
        debouncedSaveSettingsFunction: null
      }
    },
    computed: {
      ...mapGetters({
        isTutorialMode:     'mod_tutorials/getIsTutorialMode',
      }),
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

          this.debouncedSaveSettingsFunction('Computer', false);
        }
      },
      validFileExtensions() {
        let optionBasic = ['csv'];
        
        return optionBasic;
      }
    },
    watch: {
      fileList: {
        handler(newVal, prevVal) {
          if(newVal.length !== prevVal.length) {
            const fileItem = newVal.find(item => item.type == 'file');
            if (fileItem) {
              this.settings.FilePath = fileItem.path
            }

            this.Mix_settingsData_getPartitionSummary(this.currentEl.layerId);
            // update and fetch only when file is add or remove
            if(this.currentEl.layerSettings.accessProperties.Sources.length != this.settings.accessProperties.Sources.length)
              this.debouncedSaveSettingsFunction('Computer', false);

          }
        },
        deep: true,
      },
      'settings.accessProperties.Sources.length': {
        handler(newVal) {
          if(newVal) this.$nextTick(()=> { this.showBtn() });
          else this.$nextTick(()=> { this.hideBtn() });
          this.getSettingsInfo()
        },
        immediate: true
      },
      'settings.FeatureName'(newVal, oldVal) {
        if (!oldVal) { return; }
        if (newVal === oldVal) { return; }

        this.debouncedSaveSettingsFunction('Computer', false);
      },
    },
    methods: {
      getfolder(e) {
        var files = e.target.files;
        var path = files[0].webkitRelativePath;
        var Folder = path.split("/");
        console.log(files, path, Folder);
      },
      setPartitionList(list) {
        this.settings.accessProperties.Partition_list = list
      },
      openFilePicker(fileType) {
        this.showFilePicker = true;
        this.filePickerType = fileType;
      },
      addFiles() {
        this.filePickerAppendingItems = true;
        this.openFilePicker(this.filePickerType);
      },
      saveLoadFile(pathArr, type, isAppend) {
        if(isAppend) {
          const allPath = [... this.settings.accessProperties.Sources.map((el)=> el.path), ...pathArr];
          this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources([... new Set(allPath)], type)
        } else if (type === 'multimode') {
          const preppedSources = pathArr.map(p => ({ path: p.path, type: p.type }));
          this.settings.accessProperties.Sources = preppedSources;
        } else {
          this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources(pathArr, type);
        }

        this.filePickerAppendingItems = false;
      },
      clearPath() {
        this.getSettingsInfo();
      },
      closeFilePicker() {
        this.clearPath();
        this.showFilePicker = false;
      },
      getSettingsInfo() {
        if(this.settings.accessProperties.Sources.length) {

          this.Mix_settingsData_getDataMeta(this.currentEl.layerId, false)
            .then((data) => {
              if (data && data.Columns && data.Columns.length) {

                // Apply the other settings if needed.
                delete data.Columns;
                this.settings.accessProperties = {...this.settings.accessProperties, ...data};
              } else {
                // Clean up for cases where we changes data sources from
                // one with label to another without
                this.dataColumns = [];
              }
            });

        }
      },
      saveSettings(tabName, pushOntoHistory=false) {
        this.applySettings(tabName, pushOntoHistory);
      },
      hideBtn() {
        const btn = document.getElementById('js-hide-btn');
        if(btn) btn.style.cssText = 'display: none'
      },
      showBtn() {
        const btn = document.getElementById('js-hide-btn');
        if(btn) btn.style.cssText = ''
      },
      confirmFilePickerSelection(selectedItems) {
        this.showFilePicker = false;
        if (!selectedItems.length) { return; }

        if (this.filePickerType === 'file') {
          this.saveLoadFile(selectedItems, 'file', this.filePickerAppendingItems);
        } else if (this.filePickerType === 'folder') {
          this.saveLoadFile(selectedItems, 'directory', this.filePickerAppendingItems)
        } else if (this.filePickerType === 'multimode') {
          this.saveLoadFile(selectedItems, 'multimode', this.filePickerAppendingItems)
        }
      }
    }
  }
</script>
<style lang="scss" scoped>
  @import "../../../../scss/base";

  .section-data-select {
    font-size: 1.4rem;
    text-align: center;
    .btn {
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
      input[type="file"] {
        display: none;
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
      //margin-left: 1em;
    }
  }
  .settings-layer_section--data label.light-text {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 300;
    font-size: 1.1rem;
    line-height: 1.5rem;
  }
</style>
