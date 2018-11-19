<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              input.form_input(type="text" v-model="loadPath" disabled)
              button.btn.btn--primary(type="button"
              @click="loadFile"
              ) Load

      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
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
    data() {
      return {
        tabs: ['Computer', 'Cloud'],
        loadPath: 'No uploaded file'
      }
    },
    methods: {
      openLoadDialog,
      loadFile() {
        let opt = {
          title:"Load file in Data element",
          filters: [
            {name: 'Images', extensions: ['png', 'gif']},
            {name: 'Python', extensions: ['pickle', 'numpy']},
            {name: 'Text', extensions: ['txt', 'json', 'csv']},
            {name: 'Any', extensions: ['png', 'gif', 'pickle', 'numpy', 'txt', 'json', 'csv']}
          ]
        };
        this.openLoadDialog(this.saveLoadFile, opt)
      },
      saveLoadFile(pathArr) {
        this.loadPath = pathArr[0]
        // fs.readFile(pathArr[0],
        //   (err, data)=> {
        //     if(data) {
        //       let net = JSON.parse(data.toString());
        //       this.$store.commit('mod_workspace/ADD_loadNetwork', net)
        //     }
        //     else {
        //       console.error(err);
        //     }
        //   });
      },
    }
  }
</script>
