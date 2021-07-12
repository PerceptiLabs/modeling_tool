<template lang="pug">
  base-global-popup(:tab-set="popupTitle")
    template(slot="Import from-content")
      div.padding-fix
        div.import-model-tabs-wrapper
          button.import-model-tabs-button(
            :class="{'is-active': currentTab === 'local'}"
            @click="setTabType('local')"
            ) Local
          button.import-model-tabs-button(
            :class="{'is-active': currentTab === 'github'}"
            @click="setTabType('github')"
            ) GitHub
        div.import-model-box-with-border(slot="Import from-content" v-if="currentTab === 'local'")
          .form_holder
            .form_label Path:
            .form_row
              input.form_input(
                type="text"
                v-model="saveModelLocation"
                readonly
                data-testing-target="import-model-path"
                )
              button.btn.btn--dark-blue-rev(type="button" @click="openLoadModelPopup") Browse
        div(slot="Import from-content" v-if="currentTab === 'github'")
          view-loading(:isLoading="isFetching" )
          div.import-model-box-with-border
            .form_holder
              .form_label Enter a Git Repository containing your model.json:
              .form_holder.github-url-input
                .pre-input-label url
                input.form_input(type="text" v-model="githubRepositoryUrl")
          div.import-model-box-with-border
            .form_holder
              .form_label Save to:
              .form_row
                input.form_input(type="text" v-model="saveGithubModelLocation" readonly)
                button.btn.btn--dark-blue-rev(type="button" @click="openLoadGithubLocation") Browse
            div.info-box
              img.info-image(src="static/img/info.png")
              span.fz-14 If your repository contains data, it will be added <br/> to your local model folder

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
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
      popupTitle: ['Import from'],
      currentTab: 'local', // local or github
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
    })
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
      this.$store.commit('globalView/HIDE_allGlobalPopups');
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
  margin: -1rem;
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

}
.import-model-tabs-button {
  width: 50%;
  background: rgba(54, 62, 81, 0.4);
  border: 1px solid #3F4C70;
  line-height: 23px;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: normal;
  font-size: 12px;
  color: #B6C7FB;
  background-blend-mode: multiply;
  
  &.is-active {
    background: transparent;
  }

  &:not(.is-active) {
    background: #2A2F3A;
  }
}
.import-model-box-with-border {
  padding: 15px;
  padding-bottom: 10px; 
  border-bottom: 1px solid #3F4C70;
  margin-bottom: 20px;
}
.github-url-input {
  position: relative; 
  input {
    background: #202430;
    border-radius: 1px;
    height: 19px;
    line-height: 19px;
    padding-left: 45px;
    font-family: Nunito Sans;
    font-size: 12px;

    color: #E1E1E1;
  }
  .pre-input-label {
    position: absolute;
    top: 0;
    left: 0;
    border: 1px solid #3F4C70;
    box-sizing: border-box;
    border-radius: 2px 0px 0px 2px;
    height: 19px;
    font-family: Nunito Sans;
    font-size: 12px;
    line-height: 19px;
    padding: 0 10px;
    color: #C4C4C4;
    background: rgba(54, 62, 81, 0.4);
    background-blend-mode: multiply;
  }
}
.info-box {
  display: flex;
  align-items: center;
  color: #B6C7FB;
  .info-image {
    margin-right: 12px;
  }
}
</style>
