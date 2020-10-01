<template lang="pug">
  base-global-popup(
    :tab-set="popupTitle"
    )
    template(slot="Choose what to save-content")
      .settings-layer_section(v-if="!popupSettings.isFreezeInfo")
        .form_row
          .form_label Model name:
          .form_input
            input(type="text"
              v-model="settings.networkName"
              :class="{'bg-error': !settings.networkName}"
            )
      .settings-layer_section(v-if="!popupSettings.isFreezeInfo")
        .form_holder
          .form_label Model path:
          .form_row
            input.ellipsis.form_input(type="text"
            v-model="settings.networkPath"
            :class="{'bg-error': !settings.networkPath}"
            )
            button.btn.btn--dark-blue-rev(type="button" @click="openFilePicker") Browse

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        :disabled="!settings.networkPath.length"
        @click="answerPopup") Continue


</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
import { openLoadDialog, generateID } from '@/core/helpers.js'
import { pathSlash }  from "@/core/constants.js";

export default {
  name: "WorkspaceSaveNetwork",
  components: {BaseGlobalPopup},
  props: {
    popupSettings: {type: Object},
  },
  created() {
    this.settings.networkName = this.currentNetwork.networkName;
    if(this.popupSettings.isFreezeInfo) {
      // this.settings.networkPath = this.currentNetwork.networkRootFolder;
      let location = this.currentNetwork.apiMeta.location;
      const modelNameStartIndex = location.lastIndexOf('/');
      this.settings.networkPath = location;
    }
    this.$store.dispatch('mod_api/API_checkTrainedNetwork')
      .then((response)=> {
        this.settings.isSaveTrainedModel = response.result.content;
        this.existTrained = response.result.content;
      })
  },
  data() {
    return {
      popupTitle: ['Choose what to save'],
      settings: {
        networkName: '',
        networkPath: '',
        isSaveTrainedModel: false,
      },
      existTrained: false,
      promiseOk: null,
      promiseFail: null,
    }
  },
  computed: {
    currentNetwork() {
      return this.$store.getters['mod_workspace/GET_currentNetwork']
    },
    isEmptyPath() {
      return !!this.settings.networkPath.length
    }
  },
  watch: {
    'settings.networkName': {
      handler(newVal) {
        if(this.popupSettings.isSyncName)
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
      if(!this.popupSettings.isFreezeInfo) {
        this.settings.networkPath = this.settings.networkPath + pathSlash + this.settings.networkName;
      }
      this.promiseOk(this.settings);
    },
    // loadPathProject() {
    //   // doesn't do anything on the web version
    //   if(this.settings.projectPath.length) return;
    //   let opt = {
    //     title:"The folder in which the project will be saved",
    //     properties: ['openDirectory'],
    //   };
    //   openLoadDialog(opt)
    //     .then((pathArr)=> { this.settings.projectPath = pathArr[0] })
    //     .catch(()=> {})
    // },
    setPath(path) {
      if (path && path.length > 0) { 
        this.settings.networkPath = path[0];
      } else {
        this.settings.networkPath = '';
      }
    },
    openFilePicker() {
      this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.setPath});
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
