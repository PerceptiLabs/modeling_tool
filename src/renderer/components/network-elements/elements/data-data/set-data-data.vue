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
            button.btn(type="button" @click="loadFolder")
              i.icon.icon-open-folder
            span.data-select_text or
            button.btn(type="button" @click="loadFile")
              i.icon.icon-open-file
        .settings-layer_section(v-else)
          .form_row
            button.btn.btn--link(type="button" @click="clearPath")
              i.icon.icon-backward
              span Back
          .form_row
            input.form_input(type="text" v-model="inputPath" readonly="readonly")
          .form_row
            base-select
          .form_row
            chart-picture(
              v-if="imgType === 'image'"
              :disable-header="true"
              :chartData="imgData"
            )
            chart-base(
              v-if="imgType === 'line' || imgType === 'bar' || imgType === 'scatter'"
              :disable-header="true"
              :chartData="imgData"
            )
            chart-heatmap(
              v-if="imgType === 'heatmap'"
              :disable-header="true"
              :chartData="imgData"
            )

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-cloud
    .settings-layer_foot
      button.btn.btn--primary(type="button"
        v-show="settings.accessProperties.Path.length"
        @click="applySettings"
        ) Apply

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCloud  from '@/components/network-elements/elements-settings/setting-clouds.vue';
  import {openLoadDialog} from '@/core/helpers.js'

  import requestApi   from "@/core/api.js";
  import ChartPicture from "../../../charts/chart-picture";
  import ChartBase from "../../../charts/chart-base";
  import ChartHeatmap from "../../../charts/chart-heatmap";

  export default {
    name: 'SetDataData',
    mixins: [mixinSet],
    components: {ChartHeatmap, ChartBase, ChartPicture, SettingsCloud },
    props: {
      layerId: {
        type: String,
        default: ''
      }
    },
    mounted() {

    },
    data() {
      return {
        tabs: ['Computer', 'Cloud'],
        coreCode: '',
        imgData: null,
        imgType: '',
        settings: {
          Type: 'Data',
          accessProperties: {
            Category:'Local',
            Type: 'Data',
            Path: [],
          }
        }
      }
    },
    computed: {
      appPath() {
        return this.$store.getters['globalView/GET_appPath']
      },
      isDisabled() {
        return process.env.NODE_ENV === 'production'
      },
      currentNetworkID() {
        return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
      },
      inputPath() {
        return this.settings.accessProperties.Path.join(', ')
      }
    },
    watch: {
      'settings.accessProperties.Path': {
        handler(newVal) {
          if(newVal) {
            this.getDataImg()
          }
        },
        immediate: true
      }
    },
    methods: {
      openLoadDialog,
      loadFile() {
        let opt = {
          title:"Load file or files",
          properties: ['openFile', 'multiSelections'],
          filters: [
            {name: 'All', extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'txt', 'json', 'csv', 'mat', 'npy', 'npz']},
            {name: 'Images', extensions: ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff']},
            {name: 'Text', extensions: ['txt', 'json', 'csv', 'mat', 'npy', 'npz']},
          ]
        };
        this.openLoadDialog(this.saveLoadFile, opt)
      },
      loadFolder() {
        let opt = {
          title:"Load folder",
          properties: ['openDirectory']
        };
        this.openLoadDialog(this.saveLoadFile, opt)
      },
      saveLoadFile(pathArr) {
        this.settings.accessProperties.Path = pathArr;
        //this.applySettings();
        //this.$store.dispatch('mod_workspace/SET_elementSettings', this.settings)
      },
      clearPath() {
        this.settings.accessProperties.Path = [];
      },
      getDataImg() {
        let theData = {
          reciever: this.currentNetworkID,
          action: 'getDataPlot',
          value: {
            Id: this.layerId,
            Type: 'DataData',
            Properties: this.settings
          }
        };
        console.log('send ', theData);
        const client = new requestApi();
        client.sendMessage(theData)
          .then((data)=> {
            if(data === 'Null') {
              return
            }
            console.log(data);
            this.imgType = data.series[0].type;
            this.imgData = data;

            // if(view.length) {
            //   this.$set(this.chartData, view, data)
            // }
            // else this.chartData = data;
          })
          .catch((err)=> {
            console.log('answer err');
            console.error(err);
          });
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