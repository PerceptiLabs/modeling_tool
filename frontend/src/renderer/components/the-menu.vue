<template lang="pug">
  nav.app-header_nav(
    v-hotkey="keymap"
    )
    ul.header-nav
      li.header-nav_item(
      v-for="(item, i) in navMenu"
      :key="i"
      )
        button.btn.btn--link.header-nav_btn(type="button"
          v-if="item.visible"
        ) {{ item.label }}
        ul.header-nav_sublist.sublist--top(
          :data-tutorial-marker="'MenuItem_' + item.label"
          :data-testing-target="'MenuItem_' + item.label"
        )
          li.header-nav_item(
            v-for="(subItem, index) in item.submenu"
            :key="subItem.index"
          )
            div.separator(v-if="subItem.type === 'separator'")
            button.btn.btn--link.header-nav_sublist-btn(type="button"
              v-if="(!('visible' in subItem) || subItem.visible) && subItem.type !== 'separator'"
              :disabled="subItem.enabled === false"
              @click="(ev) => subItem.active(ev, false)"
            )
              span.header-nav_btn-text {{ subItem.label }}
              span.text-disable.hotkey(
                v-if="subItem.accelerator"
                ) {{ subItem.accelerator }}
              i.icon.icon-shevron-right(
                v-if="subItem.submenu"
                )
</template>

<script>
  import { mapGetters, mapMutations, mapActions, mapState } from 'vuex';
  import {baseUrlSite, MODAL_PAGE_PROJECT, PERCEPTILABS_DOCUMENTATION_URL} from '@/core/constants.js';
  import { goToLink, isOsMacintosh } from '@/core/helpers.js'
 
export default {
  name: "TheMenu",
  mounted() {
  },
  data() {
    return {
      dataKeymap: {},
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:             'mod_tutorials/getIsTutorialMode',
      isLogin:                    'mod_user/GET_userIsLogin',
      networkHistory:             'mod_workspace-history/GET_currentNetHistory',
      isDefaultProjectMode:       'mod_project/GET_isDefaultProjectMode',
      currentModel:               'mod_workspace/GET_currentNetwork',
    }),
    ...mapState({
      currentProjectId:           state => state.mod_project.currentProject,
      isSettingInputFocused:      state => state.mod_workspace.isSettingInputFocused,
      viewType:                   state => state.mod_workspace.viewType,
    }),
    statusLocalCore() {
      return this.$store.state.mod_api.statusLocalCore;
    },    
    isTutorialActive() {
      return this.isTutorialMode || this.isStoryBoard;
    },
    showExport() {
      return !process.env.NO_KC;
    },
    openApp() {
      return this.$store.state.globalView.appIsOpen
    },

    isMac() {
      return isOsMacintosh();
    },
    navMenu() {
      return this.navMenuWeb()
    },
    keymap () {
      this.navMenu.forEach((item) => {
        item.submenu.forEach((subItem) => {
          if(subItem.accelerator) {
            this.dataKeymap[subItem.accelerator] = (ev) => subItem.active(ev, true)
          }
        })
      });
      return this.dataKeymap;
    },
    isDisabledPrevStep() {
      const history = this.networkHistory;
      return !!history && history.historyStep === history.historyNet.length - 1
    },
    isDisabledNextStep() {
      const history = this.networkHistory;
      return !!history && history.historyStep === 0
    },
    hasNetworkWithUnsavedChanges() {
      return this.$store.getters['mod_workspace-changes/get_networksWithChanges'].length > 0;      
    },
    isCurrentModelOpened() {
      return this.currentModel && (
        (this.viewType === 'model' && this.currentModel.networkMeta.hideModel === false) || 
        (this.viewType === 'statistic' && this.currentModel.networkMeta.openStatistics === true && this.currentModel.networkMeta.hideStatistics === false)
      )
    }
  },
  methods: {
    ...mapMutations({
      saveNetwork:      'mod_events/set_saveNetwork',
      saveNetworkAs:    'mod_events/set_saveNetworkAs',
      setTutorialMode:  'mod_tutorials/setTutorialMode',
    }),
    ...mapActions({
      infoPopup:        'globalView/GP_infoPopup',
      popupConfirm:     'globalView/GP_confirmPopup',
      popupNewModel:    'globalView/SET_newModelPopup',
      loadNetwork:      'mod_events/EVENT_loadNetwork',
      HCCopy:           'mod_events/EVENT_hotKeyCopy',
      HCCut:           'mod_events/EVENT_hotKeyCut',
      HCPaste:          'mod_events/EVENT_hotKeyPaste',
      HCSelectAllAction:      'mod_workspace/SET_elementSelectAll',
      HCDeselectAll:    'mod_workspace/SET_elementUnselect',
      toPrevStepHistoryMutation:'mod_workspace-history/TO_prevStepHistory',
      toNextStepHistoryMutation:'mod_workspace-history/TO_nextStepHistory',
      setActivePageAction: 'modal_pages/setActivePageAction',
      setCurrentView:   'mod_tutorials/setCurrentView'
    }),
    HCSelectAll() {
      if(!this.isSettingInputFocused) {
        this.HCSelectAllAction()
      }
    },
    goToLink,
    addNewNetwork() {
      if (this.$route.name !== 'projects') {
        this.$router.push({name: 'projects'});
      }
    },
    logOut() {
      if (this.hasNetworkWithUnsavedChanges) {
        this.popupConfirm(
          {
            text: 'You still have unsaved models.\nAre you sure you want to log out?',
            ok: () => {
              this.$store.dispatch('mod_events/EVENT_logOut');
            }
          });
      } else{
        this.$store.dispatch('mod_events/EVENT_logOut');
      }
    },
    goToHelpPageDesktop() {
      this.goToLink(`${baseUrlSite}/i_docs`);
    },
    goToAboutPageDesktop() {
      this.goToLink(`${baseUrlSite}/about`);
    },
    goToHelpPageWeb() {
       this.goToLink(PERCEPTILABS_DOCUMENTATION_URL);
    },
    goToAboutPageWeb() {
      this.$store.commit('globalView/set_showAppAbout', true);
    },
    newModel() {
      this.popupNewModel(true);
    },
    openLoadModelPopup() {
      this.$store.dispatch('globalView/SET_showImportNetworkfromGitHubOrLocalPopup', true);
    },
    openLoadPbPopup() {
      this.$store.dispatch('globalView/SET_filePickerPopup', {
        filePickerType: 'file',
        confirmCallback: this.onLoadPbComplete
      });
    },
    onLoadPbComplete(path) {
      console.log('onLoadPbComplete', path);
      this.$store.dispatch('mod_api/API_parse', path);
    },
    saveModel() {
      this.saveNetwork();
    },
    saveModelAs() {
      this.saveNetworkAs();
    },
    exportModel() {
      this.$store.dispatch('globalView/SET_exportNetworkPopup', true);
    },
    exportModelToGithub() {
      this.$store.dispatch('globalView/SET_exportNetworkToGithubPopup', true);
    },
    HC_delete() {
      this.$store.dispatch('mod_events/EVENT_pressHotKey', 'del')
    },
    HC_esc() {
      this.$store.dispatch('mod_events/EVENT_hotKeyEsc')
    },
    HC_addLayerContainer() {
      if(this.openApp) this.$store.dispatch('mod_workspace/ADD_container');
    },
    HC_unGroupLayerContainer() {
      this.$store.dispatch('mod_workspace/UNGROUP_container');
    },
    toPrevStepHistory(ev) {
      ev.preventDefault();
      if (!this.isDisabledPrevStep) {
        this.toPrevStepHistoryMutation();
      }
    },
    onPaste(ev, triggeredByHotkey) {
      if (!Array.from(document.activeElement.classList).includes('inputarea')) {
        ev.preventDefault();
      }
      
      this.HCPaste(triggeredByHotkey);
    },
    toNextStepHistory(ev) {
      ev.preventDefault();
      if(!this.isDisabledNextStep) {
        this.toNextStepHistoryMutation()
      }
    },
    setActivePage() {
      this.setActivePageAction(MODAL_PAGE_PROJECT);
    },
    navMenuWeb() {
      return [
        {
            label: 'PerceptiLabs',
            submenu: []
        },
        {
          label: 'File', visible: true,
          submenu: [
            {label: 'New',             active: this.newModel},
            {type: 'separator'},
            {label: 'Import Model',    active: this.openLoadModelPopup},
            ...(this.isDefaultProjectMode ?
              [] :
              [{label: "View Projects", active: this.setActivePage},]
            ),
            {type: 'separator'},
            {label: 'Save',         accelerator: this.isMac ? 'meta+s' : 'ctrl+s',              enabled: this.openApp,  active: this.saveModel },
            {label: 'Save as',   accelerator: this.isMac ? 'meta+shift+s' : 'ctrl+shift+s',     enabled: this.openApp,  active: this.saveModelAs },
            {type: 'separator'},
            {label: 'Export',  active: this.exportModel,        enabled: this.isCurrentModelOpened && this.openApp},
            {label: 'Export to GitHub',  active: this.exportModelToGithub,        enabled: this.isCurrentModelOpened && this.openApp && this.showExport, visible: this.showExport},
            {type: 'separator'},
            {label: 'Log out', active: this.logOut,             enabled: this.isLogin},
          ]
        },
        {
          label: 'Edit', visible: true,
          submenu: [
            {label: 'Undo',         accelerator: this.isMac ? 'meta+z' : 'ctrl+z',              role: 'undo',       enabled: this.openApp,        active: this.toPrevStepHistory },
            {label: 'Redo',         accelerator: this.isMac ? 'meta+shift+z' : 'ctrl+y',  role: 'redo',       enabled: this.openApp,        active: this.toNextStepHistory },
            {type:  'separator'},

            {label: 'Cut',          accelerator: this.isMac ? 'meta+x' : 'ctrl+x',              role: 'cut',        enabled: this.openApp,        active: this.HCCut },
            {label: 'Copy',         accelerator: this.isMac ? 'meta+c' : 'ctrl+c',              role: 'copy',       enabled: this.openApp,        active: this.HCCopy },
            {label: 'Paste',        accelerator: this.isMac ? 'meta+v' : 'ctrl+v',              role: 'paste',      enabled: this.openApp,        active: this.onPaste },

            {type:  'separator'},
            {label: 'Select all',   accelerator: this.isMac ? 'meta+a' : 'ctrl+a',              role: 'selectAll',  enabled: this.openApp,        active: this.HCSelectAll },
            {label: 'Deselect all', accelerator: this.isMac ? 'meta+shift+a' : 'ctrl+shift+a',                      enabled: this.openApp,        active: this.HCDeselectAll },

          ]
        },
        {
          role: 'help',
          label: 'Help', visible: true,
          submenu: [
            {label: 'Help',                                                           active: this.goToHelpPageWeb },
            {label: 'About',                                                          active: this.goToAboutPageWeb },
          ]
        },
        {
          label: '', visible: false,
          submenu: [
            {type:  'separator'},
            {label: 'Delete',       accelerator: this.isMac ? 'meta+backspace' : 'delete',                              active: this.HC_delete,                    visible: false  },
            {label: 'DeleteMac',    accelerator: this.isMac ? 'backspace' : '',                              active: this.HC_delete,                    visible: false  },
            // {label: 'Add group',    accelerator: this.isMac ? 'meta+g' : 'ctrl+g',              enabled: this.openApp,  active: this.HC_addLayerContainer,         visible: false  },
            // {label: 'Ungroup',      accelerator: this.isMac ? 'meta+shift+g' : 'ctrl+shift+g',  enabled: this.openApp,  active: this.HC_unGroupLayerContainer,     visible: false  },
            {type:  'separator'},
            {label: 'Close setting popups',          accelerator: 'esc',                                                active: this.HC_esc,                       visible: false  },
          ]
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .app-header_nav {
    height: 100%;
    -webkit-app-region: no-drag;
  }
  .app-header--hidden {
    position: absolute;
    opacity: 0;
    left: -9999px;
    width: 1px;
    height: 1px;
    overflow: hidden;
  }
  .header-nav {
    font-weight: 500;
    display: flex;
    height: 100%;
    > .header-nav_item {
      font-size: 14px;
      color: $col-txt;
      color: #CDD8F8;
      display: flex;
      align-items: center;
      &:hover {
        background: $disable-txt;
      }
    }
  }
  .header-nav_item {
    color: $white;
    position: relative;
    &:hover > .header-nav_sublist {
      display: block;
    }
    .is-web & {
      &:hover > .header-nav_sublist {
        display: block;
      }
    }
  }
  .header-nav_btn {
    padding: 0 1rem;
    -webkit-app-region: no-drag;
  }
  .header-nav_sublist {
    display: none;
    font-weight: 400;
    position: absolute;
    z-index: 1;
    min-width: 20rem;
    background-color: $bg-workspace;
    box-shadow: $box-shad;
    &.sublist--top {
      top: 100%;
    }
    &.sublist--right {
      top: 0;
      left: 100%;
    }
    .separator {
      height: 1px;
      margin: .25rem 2px;
      background: #141419;
    }
  }
  .header-nav_sublist-btn {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: .7rem 2rem;
    text-align: left;
    white-space: nowrap;
    border-radius: 0;
    &:hover {
      background: rgba(#6185EE, .5)
    }
    .text-disable {
      flex: 0 0 auto;
    }
  }
  .header-nav_btn-text {
    padding-right: 1rem;
    flex: 1 1 100%;
  }
  .hotkey{
    text-transform: capitalize;
  }
</style>
