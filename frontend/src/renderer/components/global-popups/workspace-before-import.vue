<template lang="pug">
  base-global-popup(:tab-set="popupTitle")
    template(slot="Parser-content")
      .form_row
        .form_label Trainable:
        .form_input
          base-select(
            v-model="settings.Trainable"
            :select-options="trainLayers"
          )
      .form_row
        .form_label Create containers:
        .form_input
          base-checkbox(group-name="group" v-model="settings.Containers")
      .form_row
        .form_label End points:
        .form_input
          input(type="text" v-model="settings.EndPoints")
      .form_row
        .form_label Pb or pbtxt:
        .form_input
          input.ellipsis--right(type="text" readonly="true"
            v-model="settings.Pb"
            :class="{'bg-error': !settings.Pb.length}"
            @click="loadPbFile"
            )
      .form_row
        .form_label Checkpoint:
        .form_input
          input.ellipsis--right(type="text" readonly="true"
            v-model="settings.Checkpoint"
            @click="loadCheckpointFile"
            )


    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup"
        ) Cancel
      button.btn.btn--primary(type="button"
        @click="applySet"
        ) Confirm


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
      popupTitle: ['Parser'],
      trainLayers: [
        { text: 'All', value: 'All' },
        { text: 'Last', value: 'Last' },
        { text: 'None', value: 'None' },
      ],
      settings: {
        Trainable: 'All',
        Containers: true,
        EndPoints: '',
        Pb: '',
        Checkpoint: ''
      }
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:  'mod_tutorials/pointActivate',
      sendParseModel:         'mod_api/API_parse',
    }),
    applySet() {
      this.closePopup();
      this.$store.commit('mod_workspace/SET_showStartTrainingSpinner', true);
      this.sendParseModel(this.settings)
        .then(()=> { this.$store.commit('mod_workspace/SET_showStartTrainingSpinner', false) })
        .catch(()=> {})
    },
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
    loadPbFile() {
      //this.$store.commit('globalView/GP_showWorkspaceBeforeImport', false);
      let opt = {
        title:"Load Pb File",
        properties: ['openFile'],
        filters: [
          {name: 'All', extensions: ['pb', 'pbtxt', 'pb.*', 'pbtxt.*']},
        ]
      };
      openLoadDialog(opt)
        .then((pathArr)=> { this.settings.Pb = pathArr })
        .catch(()=> {})
    },
    loadCheckpointFile() {
      //this.$store.commit('globalView/GP_showWorkspaceBeforeImport', false);
      let opt = {
        title:"Load Checkpoint",
        properties: ['openFile'],
        filters: [
          {name: 'All', extensions: ['ckpt', 'ckpt.*']},
        ]
      };
      openLoadDialog(opt)
        .then((pathArr)=> { this.settings.Checkpoint = pathArr })
        .catch(()=> {})
    },
  }
}
</script>

<style lang="scss" scoped>
  .settings-layer_section {
    width: 100%;
  }
  .btn--dark-blue {
    height: 3rem;
    &:hover {
      background: #E1E1E1;
    }
  }
</style>
