<template lang="pug">
  base-global-popup(
    :title="popupTitle"
    title-align="text-center"
    @closePopup="closePopup"
  )
    template(slot="Import from-content")
      div.padding-fix
        div.import-model-tabs-wrapper          
          div.bold Local
          base-toggle.toggle(:value="isGithub" :isOne="false" styling="large" :onClick="() => {this.isGithub = !this.isGithub}")
          div.bold GitHub
          
        div.import-model-box-with-border(slot="Import from-content" v-if="currentTab === 'local'")
          .form_holder
            .form_label.bold Path:
            .form_input.input_group.form_row
              input.form_input(
                type="text"
                v-model="saveModelLocation"
                readonly
                data-testing-target="import-model-path"
                )
              button.btn.btn--primary(type="button" @click="openLoadModelPopup") Browse
        div(slot="Import from-content" v-if="currentTab === 'github'")
          view-loading(:isLoading="isFetching" )
          div.import-model-box-with-border
            .form_holder
              .form_label Enter a Git Repository containing your model.json:
              .form_input.input_group.form_row
                .pre-input-label url
                input.form_input(type="text" v-model="githubRepositoryUrl")
          div.import-model-box-with-border
            .form_holder
              .form_label Save to:
              .form_input.input_group.form_row
                input.form_input(type="text" v-model="saveGithubModelLocation" readonly)
                button.btn.btn--primary(type="button" @click="openLoadGithubLocation") Browse
            div.info-box
              img.info-image(src="static/img/info.png")
              span.fz-14 If your repository contains data, it will be added <br/> to your local model folder

    template(slot="action")
      button.btn.btn--secondary(type="button"
        @click="closePopup") Cancel
      button.btn.btn--primary(type="button"
        @click="onImportHandleType") Import


</template>

<script>
import { isWeb } from "@/core/helpers";
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
import BaseAccordion    from "@/components/base/accordion.vue";
import ViewLoading from '@/components/different/view-loading.vue'
import { mapActions, mapState, mapGetters } from 'vuex'
import { importRepositoryFromGithub as rygg_importRepositoryFromGithub } from '@/core/apiRygg.js';
export default {
  name: "ImportModel",
  components: { BaseGlobalPopup, BaseAccordion, ViewLoading },
  data() {
    return {
      popupTitle: 'Import from',
      isGithub: false,
      // currentTab: 'local', // local or github
      settings: {
        name: '',
        includeTensorflowFiles: true,
        includeDataFiles: true,
      },
      saveModelLocation: '',
      saveGithubModelLocation: '',
      githubRepositoryUrl: 'http://www',
      isFetching: false,
    }
  },
  computed: {
    ...mapState({
      currentProjectId: state => state.mod_project.currentProject
    }),
    ...mapGetters({
      projectPath: 'mod_project/GET_projectPath',
    }),
    currentTab () {
      return this.isGithub ? 'github' : 'local'
    }
  },
  mounted() {
    this.settings.name = this.$store.getters['mod_workspace/GET_currentNetwork'].networkName
    this.saveGithubModelLocation = this.projectPath
  },
  methods: {
    ...mapActions({
        loadNetwork:      'mod_events/EVENT_loadNetwork',
    }),
    setTabType(tabType) {
      this.currentTab = tabType;
    },
    closePopup() {
      this.$store.commit('globalView/set_showImportNetworkfromGitHubOrLocalPopup', false);
    },
    openLoadGithubLocation() {
      this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.setGithubModelLocationPath});
    },
    setGithubModelLocationPath(path) {
      this.saveGithubModelLocation = path[0]
    },
    openLoadModelPopup() {
       this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.setImportModelLocationPath});
    },
    setImportModelLocationPath(path) {
      this.saveModelLocation = path[0]
    },
    onImportHandleType() {
      switch (this.currentTab) {
        case 'local': {
          this.onLoadNetworkConfirmed(this.saveModelLocation);
          break;
        }
        case 'github' : {
          this.importRepositoryFromGithubAction();
          break;
        }
      }
    },
    onLoadNetworkConfirmed(path) {
      if (!path || path.length === 0) { return; }

      this.$store.dispatch('globalView/SET_filePickerPopup', false);
    
      this.loadNetwork(path);
      this.$store.dispatch('globalView/SET_showImportNetworkfromGitHubOrLocalPopup', false);
      this.$store.dispatch('mod_empty-navigation/SET_emptyScreenMode', 0);
      this.$store.dispatch('mod_workspace/setViewType', 'model');
    },
    importRepositoryFromGithubAction() {
      const path = this.saveGithubModelLocation
      const url = this.githubRepositoryUrl
      const overwrite = true;

      const repositoyName = url.slice(url.lastIndexOf('/')+1);
      this.isFetching = true;
      rygg_importRepositoryFromGithub({path, url, overwrite})
        .then(() => {
          const saveToPath = this.saveGithubModelLocation;
          this.onLoadNetworkConfirmed(saveToPath + '/' + repositoyName);
        })
        .catch(err => {
          console.log(err)
          const msg = (!!err.userMessage) ?
          `Importing failed. <br />${err.userMessage}`:
          `Importing failed.`
          this.$store.dispatch('globalView/GP_errorPopup', msg)
        })
        .finally(() => {
          this.isFetching = false;
        });
    }
   }
}
</script>

<style lang="scss" scoped>
.padding-fix {
  // margin: -1rem;
  margin-top: 30px;
}
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
.import-model-tabs-wrapper {
  display: flex;  
  justify-content: center;
  align-items: center;
  font-size: 16px;
  margin-bottom: 10px;
}
.import-model-box-with-border {
  padding: 15px;
  padding-bottom: 10px; 
  border-bottom: $border-1;
  margin-bottom: 20px;
}
.info-box {
  display: flex;
  align-items: center;
  .info-image {
    margin-right: 12px;
  }
}
.toggle {
  margin: 0 10px;
}
.pre-input-label {
  width: 40px;
  height: 38px;
  font-size: 16px;
  line-height: 38px;
  text-align: center;
  border-right: $border-1 !important;
}
</style>
