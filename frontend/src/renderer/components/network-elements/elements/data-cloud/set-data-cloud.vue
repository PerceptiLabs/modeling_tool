<template lang="pug">
  net-base-settings(
    :tab-set="dynamicTabs"
    :current-el="currentEl"
    id-set-btn="tutorial_button-apply"
    @press-apply="login($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Cloud-content")
      .settings-layer_section.section-data-select(v-if="settings.step === 'button'")
        button.btn(type="button"
          @click="openAWSform"
        )
          i.icon.icon-bucket
          span AWS Bucket

      template(v-else-if="settings.step === 'authorization'")
        .settings-layer_section
          .form_row
            .form_awd_label Bucket:
            .form_holder.awd_bucket_input.long
              input(type="text" placeholder="specify field entry")
            .form_holder.awd_bucket_input.short
              input(type="text" placeholder="optional tags")
        .settings-layer_section
          .form_row
            .form_holder
              .form_label-full-width AWS Access Key ID
              input(type="text")
          .form_row
            .form_holder
              .form_label-full-width AWS Secret Access Key
              input(type="text")

      template(v-else-if="settings.step === 'settings'")
        .settings-layer_section
          .form_row
            .form_holder.awd_bucket_input.short
              .form_label Delimiter
              input(type="text" placeholder="set delimiter")
            .form_holder.awd_bucket_input.long
              .form_label Prefix
              input(type="text" placeholder="type prefix to search")
          .form_holder
            .form_label-full-width Matched File List:
            ul.setting-app-list
              li.setting-app-list_item(v-for="item in modelList")
                base-checkbox(v-model="item.model") {{item.path}}


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

  import { mapGetters }     from 'vuex';

  export default {
    name: 'SetDataCloud',
    mixins: [mixinSet, mixinData],
    components: {ChartSwitch, SettingsCloud, TripleInput, SettingsFileList },
    mounted() {
      if(this.settings.accessProperties.Columns.length) {
        this.dataColumnsSelected = this.settings.accessProperties.Columns;
      }
      this.Mix_settingsData_getDataMeta(this.currentEl.layerId)
        .then((data)=> {
          if (data.Columns && data.Columns.length) this.createSelectArr(data.Columns);
        });
    },
    data() {
      return {
        //tabs: ['Computer', 'Cloud'],
        //tabs: ['Computer', 'Code'],
        dataColumns: [],
        dataColumnsSelected: [],
        interactiveInfo: {
          folder: {
            title: 'Select Folder',
            text: 'Select a folder where the data is stored'
          },
          file: {
            title: 'Select File',
            text: 'Select a data file'
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
          },
          step: 'button' // authorization //settings
        },
        modelList: [
          {
            path: 'metadata/name1',
            model: ''
          },
          {
            path: 'metadata/name2',
            model: ''
          },
          {
            path: 'metadata/name3',
            model: ''
          },
          {
            path: 'metadata/name4',
            model: ''
          }
        ]
      }
    },
    computed: {
      ...mapGetters({
        appPath:        'globalView/GET_appPath',
        isTutorialMode: 'mod_tutorials/getIsTutorialMode',
      }),
      dynamicTabs() {
        return this.settings.accessProperties.Sources.length ? ['Cloud', 'Code'] : ['Cloud']
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
          else this.$nextTick(()=> { this.hideBtn() })
        },
        immediate: true
      }
    },
    methods: {
      setPartitionList(list) {
        this.settings.accessProperties.Partition_list = list
      },
      openAWSform() {
        this.settings.step = 'authorization';
        this.showBtn();
      },
      login(tabName) {
        this.settings.step = 'settings';
        //this.applySettings(tabName);
      },
      addFiles() {
        if(this.typeOpened === 'file') this.loadFile(true);
        else this.loadFolder(true)
      },
      saveLoadFile(pathArr, type, isAppend) {
        if(isAppend) {
          const allPath = [... this.settings.accessProperties.Sources.map((el)=> el.path), ...pathArr];
          this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources([... new Set(allPath)], type)
        }
        else this.settings.accessProperties.Sources = this.Mix_settingsData_prepareSources(pathArr, type);
        this.getSettingsInfo();
      },
      clearPath() {
        this.Mix_settingsData_deleteDataMeta('DataData')
          .then(()=> {
            this.settings.accessProperties.Sources = [];
            this.getSettingsInfo()
          })
          .catch((err)=> console.log(err))
      },
      getSettingsInfo() {
        if(this.settings.accessProperties.Sources.length) {
          this.Mix_settingsData_dataSettingsMeta('DataData')
            .then((data)=> {
              if (data.Columns && data.Columns.length) {
                this.createSelectArr(data.Columns);
                return data
              }
            })
        }
      },
      createSelectArr(data) {
        let selectArr = [];
        data.forEach((el, index)=> selectArr.push({text: el, value: index}));
        this.dataColumns = [...selectArr];
        this.dataColumnsSelected.push(this.dataColumns[0].value);
      },
      hideBtn() {
        document.getElementById('js-hide-btn').style.cssText = 'display: none'
      },
      showBtn() {
        document.getElementById('js-hide-btn').style.cssText = ''
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
  .setting-app-list {
    border-radius: 5px;
    font-size: 1.4rem;
    width: 100%;
    max-height: 20rem;
    overflow-y: auto;
  }
  .setting-app-list_item {
    background: $bg-input;
    margin-bottom: 1px;
    display: block;
    padding: 0.7rem;
  }
  .form_label-full-width {
    max-width: 100%;
    margin-bottom: 0.5rem;
    font-size: 1.4rem;
  }
  .form_awd_label {
    font-size: 1.4rem;
    margin-right: 1rem;
  }
  .awd_bucket_input {
    margin: 0.5rem;
    & input::-webkit-input-placeholder {
      color: $bg-scroll;
    }
    &.short {
      width: 45%;
    }
    &.long {
      width: 55%;
    }
  }

  .section-data-select {
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

</style>
