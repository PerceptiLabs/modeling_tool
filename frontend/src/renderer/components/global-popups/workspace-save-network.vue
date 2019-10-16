<template lang="pug">
  base-global-popup(
    :tab-set="popupTitle"
    )
    template(slot="Choose what to save-content")
      .settings-layer_section(v-if="!freezeInfo")
        .form_row
          .form_label Project name:
          .form_input
            input(type="text"
              v-model="settings.projectName"
              :readonly="isEmptyPath"
              :class="{'bg-error': !settings.projectName}"
            )
      .settings-layer_section(v-if="!freezeInfo")
        .form_row
          .form_label Project path:
          .form_input
            input.ellipsis(type="text"
              v-model="settings.projectPath"
              :readonly="isEmptyPath"
              :class="{'bg-error': !settings.projectPath}"
              @click="loadPathProject"
            )
      .settings-layer_section
        .form_row
          .form_label Save settings:
          .form_input
            base-radio(group-name="group" :value-input="false" v-model="settings.isSaveTrainedModel")
              span Save only model
            base-radio(group-name="group" :value-input="true" v-model="settings.isSaveTrainedModel" :disabled="!existTrained")
              span Save trained network

    template(slot="action")
      button.btn.btn--primary(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        :disabled="!settings.projectPath.length"
        @click="answerPopup") Continue


</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
import { openLoadDialog, generateID } from '@/core/helpers.js'

export default {
  name: "WorkspaceSaveNetwork",
  components: {BaseGlobalPopup},
  props: {
    existTrained: { type: Boolean },
    freezeInfo: { type: Boolean },
  },
  created() {
    console.log('currentNetwork', this.currentNetwork);
    this.settings.projectName = this.currentNetwork.networkName;
    this.settings.isSaveTrainedModel = this.existTrained;
    if(this.freezeInfo) {
      this.settings.projectPath = this.currentNetwork.networkRootFolder;
    }
  },
  // mounted() {
  //   console.log('currentNetwork', this.currentNetwork);
  //
  // },
  data() {
    return {
      popupTitle: ['Choose what to save'],
      settings: {
        projectName: '',
        projectPath: '',
        //projectId: '',
        isSaveTrainedModel: true,
      },
      promiseOk: null,
      promiseFail: null,
    }
  },
  computed: {
    currentNetwork() {
      return this.$store.getters['mod_workspace/GET_currentNetwork']
    },
    isEmptyPath() {
      return !!this.settings.projectPath.length
    }
  },
  watch: {
    'settings.projectName': {
      handler(newVal) {
        this.$store.dispatch('mod_workspace/SET_networkName', newVal)
      }
    }
  },
  methods: {
    openPopup() {
      return new Promise((resolve, reject) => {
        this.promiseOk = resolve;
        this.promiseFail = reject;
      });
    },
    closePopup() {
      this.promiseFail(false)
    },
    answerPopup() {
      //this.settings.projectId = this.saveProjectId;
      this.promiseOk(this.settings);
    },
    loadPathProject() {
      if(this.settings.projectPath.length) return;
      let opt = {
        title:"The folder in which the project will be saved",
        properties: ['openDirectory'],
      };
      openLoadDialog(opt)
        .then((pathArr)=> { this.settings.projectPath = pathArr[0] })
        .catch(()=> {})
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
