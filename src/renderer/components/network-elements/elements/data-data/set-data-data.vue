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
        .settings-layer
          .settings-layer_section
            .form_row
              input.form_input(type="text" v-model="settings.accessProperties.Path")
              button.btn.btn--primary(type="button" @click="loadFile") Load
          .settings-layer_section
            .form_row
              .form_label Data type:
              .form_input
                base-radio(groupName="group" valueInput="Data" v-model="settings.accessProperties.Type")
                  span Data
                base-radio(groupName="group" valueInput="Labels" v-model="settings.accessProperties.Type")
                  span Labels
          .settings-layer_foot
            button.btn.btn--primary(type="button" @click="applySettings") Apply
      .popup_body(:class="{'active': tabSelected == 1}")
        settings-cloud

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCloud  from '@/components/network-elements/elements-settings/setting-clouds.vue';
  import {openLoadDialog} from '@/core/helpers.js'
  export default {
    name: 'SetDataData',
    mixins: [mixinSet],
    components: {
      SettingsCloud
    },
    mounted() {
      // if(process.platform === 'linux') {
      //   let resPath = process.resourcesPath;
      //   let path = resPath.slice(0, resPath.indexOf('Resources'));
      //   this.settings.accessProperties.Path = path + 'mnist'
      // }
      // else {
      //   this.settings.accessProperties.Path = '..\\mnist'
      // }

      if(process.env.NODE_ENV === 'production' && !this.settings.accessProperties.Path) {
        this.settings.accessProperties.Path = this.appPath + 'core\\mnist'
      }
    },
    data() {
      return {
        tabs: ['Computer', 'Cloud'],
        settings: {
          Type: 'Data',
          accessProperties: {
            Category:'Local',
            Type: 'Data',
            Path: '',
          }
        }
      }
    },
    computed: {
      appPath() {
        return this.$store.getters['globalView/GET_appPath']
      }
    },
    methods: {
      openLoadDialog,
      loadFile() {
        let opt = {
          title:"Load file in Data element",
          properties: ['openDirectory']
          // filters: [
          //   // {name: 'Images', extensions: ['png', 'gif']},
          //   // {name: 'Python', extensions: ['pickle', 'numpy']},
          //   // {name: 'Text', extensions: ['txt', 'json', 'csv']},
          //   // {name: 'Any', extensions: ['png', 'gif', 'pickle', 'numpy', 'txt', 'json', 'csv']},
          //   {name: 'Folder', extensions: ['gz']}
          // ]
        };
        this.openLoadDialog(this.saveLoadFile, opt)
      },
      saveLoadFile(pathArr) {;
        this.settings.accessProperties.Path = pathArr[0];
        //this.applySettings();
        //this.$store.dispatch('mod_workspace/SET_elementSettings', this.settings)
      },
    }
  }
</script>
