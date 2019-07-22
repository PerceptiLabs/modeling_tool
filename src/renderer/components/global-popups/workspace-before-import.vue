<template lang="pug">
  base-global-popup(:tab-set="popupTitle")
    template(slot="Import settings-content")
      .settings-layer_section
        .form_row
          .form_label Labels:
          .form_input
            base-select(
              v-model="settings.Trainable"
              :select-options="trainLayers"
            )
      .settings-layer_section
        .form_row
          .form_label Cost function:
          .form_input
            base-radio(group-name="group" :value-input="true" v-model="settings.Containers")
              span Yes
            base-radio(group-name="group" :value-input="false" v-model="settings.Containers")
              span No
              //-Cross-Entropy
        .form_row
          .form_label Class weights:
          .form_input
            input(type="text" v-model="settings.EndPoints")


    template(slot="action")
      button.btn.btn--primary(type="button"
        @click="closePopup()") Cancel
      button.btn.btn--primary(type="button"
        @click="loadTFFiles()") Continue


</template>

<script>
import { mapActions }   from 'vuex';
import { openLoadDialog } from '@/core/helpers.js'

import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";

export default {
  name: "WorkspaceBeforeImport",
  components: {BaseGlobalPopup},
  data() {
    return {
      popupTitle: ['Import settings'],
      trainLayers: [
        { text: 'All', value: 'All' },
        { text: 'Last', value: 'Last' },
        { text: 'None', value: 'None' },
      ],
      settings: {
        Trainable: 'All',
        Containers: true,
        EndPoints: '',
      }
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
    openLoadDialog,
    loadTFFiles() {
      this.$store.commit('globalView/GP_showWorkspaceBeforeImport', false);
      let opt = {
        title:"Load TensorFlow Model",
        properties: ['openFile', 'multiSelections'],
        filters: [
          {name: 'All', extensions: ['pb', 'pbtxt', 'ckpt', 'pb.*', 'pbtxt.*', 'ckpt.*']},
        ]
      };
      this.openLoadDialog(opt)
        .then((pathArr)=>{
          this.$store.commit('mod_workspace/SET_showStartTrainingSpinner', true);
          let requestValue = {
            ...this.settings,
            Paths: pathArr
          };
          return this.$store.dispatch('mod_api/API_parse', {path: requestValue, ctx: this});
        })
        .then(()=>{
          this.$store.commit('mod_workspace/SET_showStartTrainingSpinner', false);
        })
        .catch(()=> {})
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
