<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        :class="{'disable': tabSelected != i}"
        @click="setTab(i)"
      )
        h3(v-html="tab.html")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              base-select(
                v-model="settings.accessProperties.Atari"
                :selectOptions="selectOptions"
                )

      .popup_body(
        :class="{'active': tabSelected == 1}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              input.form_input(type="text" placeholder="c:" readonly
                v-model="inputPath"
                )
              button.btn.btn--primary(type="button"
                @click="loadFile"
                :disabled="disabledBtn"
                ) Load
    .settings-layer_foot
      chart-switch(
      :disable-header="true"
      :chartData="imgData"
      )
    .settings-layer_foot
      button.btn.btn--primary(type="button" @click="applySettings") Apply

</template>

<script>
  import mixinSet   from '@/core/mixins/net-element-settings.js';
  import mixinData  from '@/core/mixins/net-element-settings-data.js';

  import {openLoadDialog} from '@/core/helpers.js'

  import ChartSwitch from "@/components/charts/chart-switch.vue";

  export default {
    name: 'SetDataEnvironment',
    mixins: [mixinSet, mixinData],
    components: { ChartSwitch },
    data() {
      return {
        disabledBtn: false,
        selectOptions: [
          { text: 'Breakout',     value: 'Breakout' },
          { text: 'BankHeist',    value: 'BankHeist' },
          { text: 'DemonAttack',  value: 'DemonAttack' }
        ],
        tabs: [
          {html: 'Gym',                                     type: 'Gym'},
          {html: '<i class="icon icon-search"></i> Unity',  type: 'Unity'}
          ],
        settings: {
          Type: 'Environment',
          accessProperties: {
            EnvType: 'Gym',
            Path: [],
            Atari: 'Breakout', //select
            Category: 'Local',
            Type: 'Data',
          }
        }
      }
    },
    watch: {
      'settings.accessProperties.Atari': {
        handler(newVal) {
          if(newVal) {
            this.getImage()
          }
        },
        immediate: true
      }
    },
    methods: {
      openLoadDialog,
      setTab(i) {
        this.tabSelected = i;
        this.settings.accessProperties.EnvType = this.tabs[i].type
      },
      getImage() {
        this.getDataImg('DataEnvironment')
      },
      saveLoadFile(pathArr) {
        this.disabledBtn = false;
        this.settings.accessProperties.Path = pathArr;
        this.getImage()
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
        this.openLoadDialog(opt)
          .then((pathArr)=> this.saveLoadFile(pathArr))
          .catch(()=> {
            this.disabledBtn = false;
          })
      }
    }
  }
</script>
