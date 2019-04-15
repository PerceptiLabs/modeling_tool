<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        :class="{'disable': tabSelected != i}"
        :disabled="tabSelected != i"
        @click="setTab(i)"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(:class="{'active': tabSelected == 0}")
        .settings-layer(v-if="!settings.accessProperties.Path.length")
          .settings-layer_section.section-data-select
            button.btn(type="button"
              :disabled="disabledBtn"
              @click="loadFolder"
              )
              i.icon.icon-open-folder
            span.data-select_text or
            button.btn(type="button"
              :disabled="disabledBtn"
              @click="loadFile"
              id="tutorial_button-load"
              class="tutorial-relative"
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
              :selectOptions="dataColumns"
              :select-multiple="true"
              )
          .form_row
            chart-switch(
              :disable-header="true"
              :chartData="imgData"
            )

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-cloud
    .settings-layer_foot
      button.btn.btn--primary(type="button"
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
  import coreRequest      from "@/core/apiCore.js";
  import {mapActions}     from 'vuex';

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
        tabs: ['Computer', 'Cloud'],
        coreCode: '',
        dataColumns: [],
        dataColumnsSelected: [],
        disabledBtn: false,
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
    watch: {
      dataColumnsSelected(newVal) {
        this.settings.accessProperties.Columns = newVal;
        this.getDataPlot('DataData')
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate: 'mod_tutorials/pointActivate'
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
        //this.applySettings();
        //this.$store.dispatch('mod_workspace/SET_elementSettings', this.settings)
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
        // this.getDataMeta('DataData')
        //   .then(()=> {
        //     this.getDataImg('DataData')
        //   })
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