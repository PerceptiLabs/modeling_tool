<template lang="pug">
  base-global-popup(:tab-set="popupTitle")
    template(slot="Export to GitHub-content")
      div.github-authentication-wrapper(v-if="!isGithubTokenSetted")
        h4.auth-text Authentication required
        a.verify-link(:href="GITHUB_AYTHORIZE_URL")  Verify
      div(v-if="isGithubTokenSetted")
        .settings-layer_section
          .name-wrapper
            .form_label.mr-10 Save as:
            .form_row.w-75
              input.form_input.input-black(type="text" v-model="settings.name")
        .horozontal-separator
        .settings-layer_section
          .form_holder
            base-checkbox(v-model="settings.includeTensorflowFiles" :isNewUi="true") Include TensorFlow Files
          .form_holder.mb-0
            base-checkbox(v-model="settings.includeDataFiles" :isNewUi="true") Include Data Files
        view-loading(:isLoading="isLoading")
        .horozontal-separator
        //- base-accordion(:accordion-title="accordionData" :isNewUi="true")
        //-   template(slot="basicSettings")
        //-     .settings-layer_section
        //-       .form_holder
        //-         base-checkbox(v-model="settings.includeTensorflowFiles" :isNewUi="true") Include Tensorflow Files
        //-       .form_holder
        //-         base-checkbox(v-model="settings.includeDataFiles" :isNewUi="true") Include Data Files
        //-   template(slot="advancedSettings")
        //-     .settings-layer_section
        //-       span advanced settings

    template(slot="action" v-if="isGithubTokenSetted")
      
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="ok") Export
    template(slot="action" v-if="!isGithubTokenSetted")
      span &nbsp;

</template>

<script>
import { isWeb } from "@/core/helpers"
import { mapGetters } from 'vuex'
import { GITHUB_AYTHORIZE_URL } from '@/core/constants.js'
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup"
import BaseAccordion    from "@/components/base/accordion.vue"
import ViewLoading from '@/components/different/view-loading.vue'
import axios from 'axios'

import { exportAsGithubRepository } from '@/core/apiFileserver';

export default {
  name: "ExportNetworkGitHub",
  components: {BaseGlobalPopup, BaseAccordion, ViewLoading},
  data() {
    return {
      isLoading: false,
      GITHUB_AYTHORIZE_URL,
      popupTitle: ['Export to GitHub'],
      settings: {
        name: '',
        includeTensorflowFiles: false,
        includeDataFiles: false,
      },
      accordionData: [
        {name: 'basicSettings' , html: 'Basic Settings'},
        {name: 'advancedSettings' , html: 'Advanced Settings'},
        //{name: 'git' , html: '<i class="icon icon-git"></i> Git'},
      ],
    }
  },
  computed: {
    ...mapGetters({
        projectPath: 'mod_project/GET_projectPath',
        currentModel: 'mod_workspace/GET_currentNetwork',

    }),
    isGithubTokenSetted() {
      return this.$store.state.mod_github.isGithubTokenSetted;
    },
    githubToken() {
      return this.$store.state.mod_github.githubToken;
    }
  },
  mounted() {
    this.settings.name = this.$store.getters['mod_workspace/GET_currentNetwork'].networkName;
    this.shouldVerifyGithubAuth = true;
  },
  methods: {
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
    getDataComponentsFilePaths() {
      const networkElementList = this.currentModel.networkElementList
      Object.values(networkElementList).map(el => console.log(el.componentName))

      const dataCompoenentsNames = ['DataData', 'DataEnvironment'];
      const filteredNetwork = Object.values(networkElementList).filter(el => dataCompoenentsNames.indexOf(el.componentName ) !== -1)
      const sources = filteredNetwork.filter(el => !!el.layerSettings).map(el => el.layerSettings.accessProperties.Sources);
      let dataComponentsSourcePaths = [];
      sources.map(sources => {
        sources.map(sourceObj => {
          dataComponentsSourcePaths.push(sourceObj.path);
        })
      })
      // console.log(dataComponentsSourcePaths);
      return dataComponentsSourcePaths;

    },
    async ok() {
      if(this.isLoading) { return }

      const  reqData = {
        path: [this.currentModel.apiMeta.location],
        model_path: "",
        data_path: this.settings.includeDataFiles ? this.getDataComponentsFilePaths() : [],
        overwrite: true,
        type: 'basic',
        repo_name: this.settings.name,
        github_token: this.githubToken,
        include_trained_model: this.settings.includeTensorflowFiles,
        commit_message: 'Perceptilabs commit message'
      }
      this.isLoading = true;
      exportAsGithubRepository(reqData)
        .then(res => {
          this.isLoading = false;
          const haveRepoNameSpaces = this.settings.name.indexOf(' ') !== -1;
          this.$store.dispatch('globalView/GP_infoPopup',`The model was exported successfully! ${haveRepoNameSpaces ? 'Spaces in the model name will be replaced with dashes': ''}`)
        }).catch(err => {
          this.isLoading = false;
          this.$store.dispatch('globalView/GP_infoPopup',`Fail on export`)
          // console.log(`${err.response.status} - ${err.response.data}`)
        })
    },
   }
}
</script>

<style lang="scss" scoped>
.name-wrapper {
  display: flex;
  align-items: center;
}
.popup-button {
  width: 9.5rem;
  height: 3.5rem;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 22px;
}
.mr-10 {
  margin-right: 10px;
}
.w-75 {
  width: 75%;
}
.github-authentication-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.auth-text {
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: normal;
  font-size: 12px;
  line-height: 16px;
  text-align: center;
  color: #C4C4C4;
  margin-bottom: 10px;
  margin-top: 15px;
}
.verify-link {
  background: #6185EE;
  border: 1px solid #6185EE;
  box-sizing: border-box;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  border-radius: 2px;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 12px;
  line-height: 16px;
  text-align: center;
  color: #FFFFFF;
  padding: 1px 23px;
}
.horozontal-separator {
  height: 1px;
  width: calc(100% + 20px);
  margin-left: -10px;
  background-color: #3F4C70;
  margin-bottom: 10px;
}
.input-black {
  background-color: #202330;
  border: none;
}
.mb-0 {
  margin-bottom: 0;
}
</style>
