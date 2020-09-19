<template lang="pug">
  .code-window-container(
    :class="{'code_full-view': fullView}"
    @focus="onFocus('code-window')"
    @blur="onBlur('code-window')"
    tabindex=0
  )
    .code-window
      .code-window-header(
        :class="headerStyle"
      )
        div
        div 
          span {{ this.currentEl.layerName }}
          span(v-if="hasUnsavedCodeChanges") *
        div
          svg.close-window(
            @click="beforeCloseWindowCheck"
            viewBox="0 0 7 8"
            fill="none"
            xmlns="http://www.w3.org/2000/svg")
            path(
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M6.81187 7.03489C7.05234 6.80548 7.06381 6.4219 6.83748 6.17816L4.48982 3.64974L6.83748 1.12132C7.06381 0.877568 7.05234 0.493997 6.81187 0.264587C6.5714 0.0351768 6.193 0.0468001 5.96667 0.290548L3.23333 3.23435C3.01664 3.46772 3.01664 3.83175 3.23333 4.06512L5.96667 7.00892C6.193 7.25267 6.5714 7.2643 6.81187 7.03489Z"
              fill="white")
            path(
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M0.188129 0.264663C-0.0523387 0.494073 -0.0638057 0.877644 0.162517 1.12139L2.51018 3.64981L0.162516 6.17823C-0.0638062 6.42198 -0.0523392 6.80555 0.188128 7.03496C0.428596 7.26437 0.807004 7.25275 1.03333 7.009L3.76667 4.0652C3.98336 3.83183 3.98336 3.4678 3.76667 3.23443L1.03333 0.290624C0.807004 0.0468761 0.428596 0.0352527 0.188129 0.264663Z"
              fill="white")
      spinner(v-if="isLoading")
      code-hq.code-window-content(
        v-else
        ref="codeEditor"
        :code="layerCode"
        :error-row="errorRow"
        @input="onContentChange"
        @focus="onFocus('mirror')"
        @blur="onBlur('mirror')"
        @save-shortcut="onSaveShortcut"
        )

      .code-window-footer
        .save-indicator(
          v-if="showSaveIndicator"
        )
          svg.checkmark(width="11" height="10" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(d="M1 4.80952L4.11538 9L10 1" stroke="#73FEBB" stroke-linecap="round" stroke-linejoin="round")
          span All changes saved
        button.revert-btn(
          @click="beforeCloseWindowCheck"
        ) Cancel
        button.save-btn(
          @click="onSaveClick"
        ) Save

</template>

<script>
import Spinner   from '@/components/different/start-training-spinner.vue'
import codeHq from "@/components/network-elements/elements-settings/code-hq.vue";
import { deepCopy, layerBgColorTransparent } from "@/core/helpers.js";

export default {
  name: "CodeWindow",
  components: { codeHq, Spinner },
  props: {
    networkId: {
      type: Number
    }
  },
  beforeDestroy() {
    this.closeFullView()
  },
  data() {
    return {
      fullView: false,
      layerCode: '',
      isLoading: false,
      showSaveIndicator: false,
      hasUnsavedCodeChanges: false
    }
  },
  computed: {
    currentEl() {
      if (!this.networkId) {
        return {
          layerName: '',
          componentName: '',
          layerCode: ''
        };
      }

      return this.$store.getters['mod_workspace-code-editor/getElement'](this.networkId);
    },
    currentNetwork() {
      return this.$store.getters['mod_workspace/GET_currentNetwork']
    },
    hasUnsavedChanges() {
      return this.$store.getters['mod_workspace-code-editor/getHasUnsavedChanges'](this.networkId);
    },
    headerStyle() {
      return layerBgColorTransparent(this.currentEl.componentName);
    },
    errorData() {
      return this.currentEl.layerCodeError || '';
    },
    errorRow() {
      return !!this.errorData ? this.errorData.Row : 0;
    }
  },
  methods: {
    initLayerCode() {
      if (!this.currentEl.layerCode) {
        // for normal elements (except for custom code)
        this.getCode();

      } else if (typeof this.currentEl.layerCode === 'object' && !this.currentEl.layerCode.Output) {
        // for custom code element, not sure why it's not a string
        this.getCode();
          
      } else {
        // when there is are confirmed code changes
        this.setCode(this.currentEl.layerCode);
      }
    },
    getCode() {

      this.isLoading = true;

      const value = {
        layerId: this.currentEl.layerId,
        settings: this.currentEl.layerSettings,
      };

      this.$store.dispatch('mod_api/API_getCode', value)
        .then((code)=> {
          this.setCode(code);
        })
        .finally(_ => {
          this.isLoading = false;
        });
    },
    setCode(objCode) {
      this.layerCode = objCode.Output;
    },
    toggleFullView() {
      this.fullView = !this.fullView;
      document.querySelector('.popup_body').classList.toggle("popup_body--show-code");
      document.querySelector('.network').classList.toggle("network--show-code");
      this.$refs.codeEditor.refresh();
    },
    closeFullView() {
      this.fullView = false;
      document.querySelector('.network').classList.remove("network--show-code");
    },
    beforeCloseWindowCheck() {
      if (this.hasUnsavedChanges) {
        this.$store.dispatch('globalView/GP_confirmPopup',
        {
          text: 'You have unsaved changes. Are you sure you want to close the editor?',
          ok: () => {
            this.closeWindow();
          }
        });
      } else {
        this.closeWindow();
      }
    },
    closeWindow() {
      this.$store.dispatch('mod_tutorials/setNextStep', 'tutorial-workspace-settings-code');
      this.$store.dispatch('mod_workspace-code-editor/closeEditor', { networkId: this.networkId });
    },
    onContentChange(content) {
      this.showSaveIndicator = false;

      if (this.layerCode !== content) {
        this.$store.commit('mod_workspace-code-editor/setHasUnsavedChanges', { 
          networkId: this.networkId, 
          hasUnsavedChanges: true 
        });

        this.hasUnsavedCodeChanges = true;
      }
      
      this.layerCode = content;
    },
    onSaveClick() {
      this.onSave();
    },
    onSaveShortcut() {
      this.onSave();
    },
    onSave() {
      this.showSaveIndicator = true;
      this.hasUnsavedCodeChanges = false;

      const saveSettings = {
        'elId': this.currentEl.layerId,
        'code': { Output: this.layerCode },
        'set': this.currentEl.layerSettings,
        'tabName': 'Code'
      };

      this.$store.commit('mod_workspace-code-editor/setHasUnsavedChanges', { 
        networkId: this.networkId, 
        hasUnsavedChanges: false 
      });
      this.$store.dispatch('mod_workspace/SET_elementSettings', deepCopy(saveSettings));
      this.$store.dispatch('mod_webstorage/saveNetwork', this.currentNetwork, {root: true});
      
      // calculating all preview vars here, can potentially refactor here:
      const fullNetworkElementList = this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
      let payload = {};
      for(let id in fullNetworkElementList) {
        payload[id] = fullNetworkElementList[id].previewVariable;
      }

      this.$store.dispatch('mod_api/API_getBatchPreviewSample', payload, {root: true})
    },
    onFocus(source) {
      this.$store.dispatch('mod_tracker/EVENT_codeEditorStartFocus');
      this.$store.commit('mod_workspace-code-editor/setIsInFocusState', true);
    },
    onBlur(source) {
      this.$store.dispatch('mod_tracker/EVENT_codeEditorStopFocus');
      this.$store.commit('mod_workspace-code-editor/setIsInFocusState', false);
    }
  },
  watch: {
    currentEl: {
      immediate: true,
      handler(newVal, oldVal) {
        this.initLayerCode();
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";

  $code-window-header-height: 2rem;
  $code-window-footer-height: 4rem;

  $code-window-height: 70%;
  $code-window-width: 70rem;

  $code-window-font-size: 1.2rem;

  svg {
    height: 0.8rem;
    width: 0.8rem;
  }

  .code-window-container {
    position: absolute;
    width: $code-window-width;
    height: $code-window-height;
    z-index: 6;

    background: #1E1E1E;

    border: 1px solid #475D9C;
    box-sizing: border-box;

    top: 0;
    right: 0;

    overflow: hidden;
  }

  .code-window {
    display: flex;
    flex-direction: column;
    
    height: 100%;
    width: 100%;

    .wrapper-training-loader {
      top: 20px;
    }
  }

  .code-window-header {
    position: relative;
      
    display: flex;
    align-items: center;
    height: $code-window-header-height;

    font-size: $code-window-font-size;

    & > * {
      flex: 1;
      display: flex;
    }
    
    & > :nth-child(2) {
      justify-content: center;
    }

    & > :last-child {
      justify-content: flex-end;
      
      & > * {
        margin-right: 1rem;
      }
    }

    .close-window {
      cursor: pointer;
    }
  }

  .code-window-content {
    position: relative;
    max-width: 100%;
    max-height: calc(100% - #{$code-window-header-height} - #{$code-window-footer-height});
    overflow-y: auto;

    box-sizing: border-box;
    background: #1E1E1E;

    padding: 1rem;

    font-size: $code-window-font-size;
  }

  .code-window-footer {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    height: $code-window-footer-height;
    margin-top: auto;

    button {
      color:white;
      width: 8rem;
      height: 2rem;
      background: #2F3851;
      border: 1px solid #444C62;
      box-sizing: border-box;
      border-radius: 2px;
    }
    .save-indicator {
      background: #131B30;
      border: 0.5px solid rgba(94, 111, 159, 0.5);
      box-sizing: border-box;
      border-radius: 1px;

      margin-left: 1rem;
      padding: 0.3rem 1rem;

      > * + * {
        margin-left: 1rem;
      }
    }
    .revert-btn {
      margin-left: auto;
    }
    .save-btn {
      background: #6185EE;
      border: 1px solid #6185EE;

      margin: 0 1rem;
    }
  }

  .code_full-view {
    display: flex;
    flex: 1;
    flex-direction: column;
    width: 100%;
    overflow: hidden;
    .code-wrap,
    .bookmark_content {
      height: 100%;
    }
  }

  .code-wrap_error-container {
    padding: 1rem;
    overflow: scroll;
    height: 100%;
  }
</style>
