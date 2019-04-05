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
              v-model="settings.accessProperties.Columns"
              :selectOptions="dataColumns"
              )
          .form_row
            chart-switch(
              :disable-header="true"
              :chartData="imgData"
            )

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-cloud
    .settings-layer_foot
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
  import coreRequest      from "@/core/apiCore.js";
  import {mapActions}     from 'vuex';

  export default {
    name: 'SetDataData',
    mixins: [mixinSet, mixinData],
    components: {ChartSwitch, SettingsCloud },
    data() {
      return {
        tabs: ['Computer', 'Cloud'],
        coreCode: '',
        dataColumns: [],
        disabledBtn: false,
        settings: {
          Type: 'Data',
          accessProperties: {
            Columns: '',
            Dataset_size: 3000,
            Category:'Local',
            Type: 'Data',
            Path: [],
          }
        }
      }
    },
    computed: {

    },
    watch: {
      'settings.accessProperties.Path': {
        handler(newVal) {
          this.getSettingsInfo()
        },
        immediate: true
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate'
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
        this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-load'})
        //this.applySettings();
        //this.$store.dispatch('mod_workspace/SET_elementSettings', this.settings)
      },
      clearPath() {
        this.settings.accessProperties.Path = [];
      },
      getSettingsInfo() {
        if(this.settings.accessProperties.Path.length == 0) return;
        this.getDataMeta()
          .then(()=> {
            this.getDataImg('DataData')
          })
      },
      getDataMeta() {
        let theData = {
          reciever: this.currentNetworkID,
          action: 'getDataMeta',
          value: {
            Id: this.layerId,
            Type: 'DataData',
            Properties: this.settings
          }
        };
        //console.log(theData);
        return this.coreRequest(theData)
          .then((data) => {
            //console.log('getDataMeta ', data);
            if (data === 'Null') {
              return
            }
            this.settings.accessProperties.Dataset_size = data.Dataset_size;
            if (data.Columns.length) {
              if (!this.settings.accessProperties.Columns) this.settings.accessProperties.Columns = data.Columns[0];
              data.Columns.forEach((el) => this.dataColumns.push({text: el, value: el}))
            }
          })
          .catch((err) => {
            console.error(err);
          });
      },
      saveSettings() {
        this.applySettings()
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