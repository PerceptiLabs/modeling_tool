<template lang="pug">
  base-global-popup(
    :title="popupTitle"
    title-align="text-center"
    @closePopup="closePopup"
    )
    template(:slot="popupTitle + '-content'")
      .settings-layer_section(v-if="!popupSettings.isFreezeInfo")
        .form_row
          .form_label Model name:
          .form_input
            input(type="text"
              v-model="settings.networkName"
              :class="{'bg-error': !settings.networkName}"
              data-testing-target="save-model-as-model-name"
            )
      .settings-layer_section(v-if="!popupSettings.isFreezeInfo")
        .form_holder
          .form_label Model path:
          .form_row.input_group
            input.ellipsis.form_input(type="text"
            v-model="settings.networkPath"
            :class="{'bg-error': !settings.networkPath}"
            data-testing-target="save-model-as-path"
            )
            button.btn.btn--primary(
              type="button"
              @click="openFilePicker"
              data-testing-target="save-model-as-browse"
              ) Browse

    template(slot="action")
      button.btn.btn--secondary(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        :disabled="!settings.networkPath.length"
        @click="answerPopup") Continue


</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
import { pathSlash }  from "@/core/constants.js";
import { pickDirectory as rygg_pickDirectory } from '@/core/apiRygg.js';

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
      popupTitle: 'Choose what to save',
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
    setPath(path) {
      if (path && path.length > 0) { 
        this.settings.networkPath = path[0];
      } else {
        this.settings.networkPath = '';
      }
    },
    async openFilePicker() {
      const selectedPath = await rygg_pickDirectory('Save workspace');
      if (selectedPath && selectedPath.path) {
        this.setPath([selectedPath.path])
      }
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
