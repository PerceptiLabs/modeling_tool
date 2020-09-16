<template lang="pug">
  nav.app-header_nav(
    :class="{'app-header--hidden': isMac && isElectron}"
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
        )
          li.header-nav_item(
            v-for="(subItem, index) in item.submenu"
            :key="subItem.index"
          )
            div.separator(v-if="subItem.type === 'separator'")
            button.btn.btn--link.header-nav_sublist-btn(type="button"
              v-else
              :disabled="subItem.enabled === false"
              @click="subItem.active"
            )
              span.header-nav_btn-text {{ subItem.label }}
              span.text-disable.hotkey(
                v-if="subItem.accelerator"
                ) {{ subItem.accelerator }}
              i.icon.icon-shevron-right(
                v-if="subItem.submenu"
                )
            //-ul.header-nav_sublist.sublist--right(v-if="subItem.submenu")
              li.header-nav_item(
                v-for="(subSubItem, ind) in subItem.submenu"
                /:key="subSubItem.ind"
              )
                button.btn.btn--link.header-nav_sublist-btn(type="button"
                  /:disabled="subSubItem.enabled === false"
                  @click="subItem.active"
                )
                  span {{subSubItem.label}}
                  span.text-disable.hotkey(
                    v-if="subSubItem.accelerator"
                  ) {{ subSubItem.accelerator }}

</template>

<script>
  import { mapGetters, mapMutations, mapActions, mapState } from 'vuex';
  import { baseUrlSite, MODAL_PAGE_PROJECT } from '@/core/constants.js';
  import { isElectron, goToLink, isOsMacintosh, isDesktopApp } from '@/core/helpers.js'
  import axios from 'axios'
  let ipcRenderer = null;
  if(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1) {
    const electron = require('electron');
    ipcRenderer = electron.ipcRenderer;
  }
export default {
  name: "TheMenu",
  mounted() {
    this.mainProcessListeners()
  },
  data() {
    return {
      dataKeymap: {},
      isElectron: isElectron(),
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:             'mod_tutorials/getIsTutorialMode',
      isStoryBoard:               'mod_tutorials/getIsTutorialStoryBoard',
      isLogin:                    'mod_user/GET_userIsLogin',
      networkHistory:             'mod_workspace-history/GET_currentNetHistory',
      isDefaultProjectMode:       'mod_project/GET_isDefaultProjectMode',
      isNotebookMode:             'mod_notebook/getNotebookMode',
    }),
    ...mapState({
      currentProjectId:           state => state.mod_project.currentProject,
      isSettingInputFocused:      state => state.mod_workspace.isSettingInputFocused,
    }),
    appVersion() {
      return this.$store.state.globalView.appVersion
    },
    isTutorialActive() {
      return this.isTutorialMode || this.isStoryBoard;
    },
    openApp() {
      return this.$store.state.globalView.appIsOpen
    },
    isMac() {
      return isOsMacintosh();
    },
    isDesktop() {
      return isDesktopApp();
    },
    navMenu() {
      if (isElectron()) {
        return this.navMenuDesktop();
      } else {
        return this.navMenuWeb();
      }
    },

    keymap () {
      this.navMenu.forEach((item) => {
        item.submenu.forEach((subItem) => {
          if(subItem.accelerator) {
            this.dataKeymap[subItem.accelerator] = subItem.active
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
  },
  watch: {
    navMenu(newMenu) {
      if(process.platform === 'darwin' && isElectron()) ipcRenderer.send('app-menu', newMenu)
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
      appClose:         'mod_events/EVENT_appClose',
      appMinimize:      'mod_events/EVENT_appMinimize',
      appMaximize:      'mod_events/EVENT_appMaximize',
      openNetwork:      'mod_events/EVENT_openNetwork',
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
    mainProcessListeners(isRemove) {
      this.navMenu.forEach((item) => {
        item.submenu.forEach((subItem) => {
          if(subItem.label) {
            if(isRemove) {
              if(isElectron())
              ipcRenderer.removeAllListeners(`menu-event-${subItem.label}`);
            }
            else {
              if(isElectron())
              ipcRenderer.on(`menu-event-${subItem.label}`, ()=> { subItem.active() });
            }
          }
        })
      });
    },
    checkUpdate() {
      if(isElectron()) {
        this.$store.commit('mod_autoUpdate/SET_showNotAvailable', true);
        ipcRenderer.send('check-update'); 
      }
    },
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
      window.location.href = 'https://join.slack.com/t/perceptilabs-com/shared_invite/zt-auchqflz-4YANlDBSyJW1qC7LdpQBSA';
    },
    goToAboutPageWeb() {
      window.location.href = 'https://perceptilabs.com/docs/overview';
    },
    openModel() {
      this.openNetwork();
    },
    newModel() {
      this.popupNewModel(true);

      this.$nextTick(() => {
        this.setCurrentView('tutorial-create-model-view');
      });
    },
    openLoadModelPopup() {
      this.$store.dispatch('globalView/SET_showImportNetworkfromGitHubOrLocalPopup', true);
    },
    // openLoadModelPopup() {
    //   debugger;
    //   if(this.isTutorialMode) {
    //     this.hideTooltip();
    //     this.popupConfirm(
    //       {
    //         text: 'Are you sure you want to end the tutorial?',
    //         ok: () => {
    //           this.offMainTutorial();
    //           this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.onLoadNetworkConfirmed});
    //         }
    //       });
    //   } else {
    //     this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.onLoadNetworkConfirmed});
    //   }
    // },
    // onLoadNetworkConfirmed(path) {
    //   if (!path || path.length === 0) { return; }

    //   this.$store.dispatch('globalView/SET_filePickerPopup', false);
      
    //   this.$store.dispatch('mod_events/EVENT_loadNetwork', path[0]);
    //   // this.$store.dispatch('mod_api/API_getModel',`${path[0]}/model.json`)
    //   //   .then(model => {
    //   //     if(model.hasOwnProperty('apiMeta')) {
    //   //       const { location } = model.apiMeta;
    //   //       delete model.apiMeta;
    //   //     }
    //   //     this.$store.dispatch('mod_project/createProjectModel',{
    //   //       name: model.networkName,
    //   //       project: this.currentProjectId,
    //   //       location: path[0],
    //   //     }).then(apiMeta => {
    //   //       this.$store.dispatch('mod_workspace/ADD_network', {network: model, apiMeta});
    //   //     });
    //   //   })
    //   //   .catch(e => console.log(e));

    //   // this.loadNetwork(path[0]);
    // },
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
    toNextStepHistory(ev) {
      ev.preventDefault();
      if(!this.isDisabledNextStep) {
        this.toNextStepHistoryMutation()
      }
    },
    setActivePage() {
      this.setActivePageAction(MODAL_PAGE_PROJECT);
    },
    navMenuDesktop() {
      return [
        ...(this.isMac ? [{
            label: 'PerceptiLabs',
            submenu: [
              { role: 'about',      active: ()=>{}},
              {label: 'Check for updates...', active: this.checkUpdate },
              { type: 'separator'},
              { role: 'services',   active: ()=>{}},
              { type: 'separator'},
              { role: 'hide',       active: ()=>{}},
              { role: 'hideothers', active: ()=>{}},
              { role: 'unhide',     active: ()=>{}},
              { type: 'separator'},
              {label: 'Quit PerceptiLabs', accelerator: 'meta+q', active: (e)=> this.appClose(e) }
            ]
          }] : []),
        {
          label: 'File', visible: true,
          submenu: [
            {label: 'New',          accelerator: this.isMac ? 'meta+n' : 'ctrl+n',              enabled: this.isLogin,  active: this.addNewNetwork },
            {label: 'Open',         accelerator: this.isMac ? 'meta+o' : 'ctrl+o',              enabled: this.isLogin,  active: this.openModel },
            {label: 'Save',         accelerator: this.isMac ? 'meta+s' : 'ctrl+s',              enabled: this.openApp,  active: this.saveModel },
            {label: 'Save as...',   accelerator: this.isMac ? 'meta+shift+s' : 'ctrl+shift+s',  enabled: this.openApp,  active: this.saveModelAs },
            {type: 'separator'},
            {label: 'Log out',                                                                  enabled: this.isLogin,  active: this.logOut },
            ...(this.isMac
              ? []
              : [{label: 'Exit', accelerator: 'alt+f4', active: (e)=> this.appClose(e) }]
            )
          ]
        },
        {
          label: 'Edit', visible: true,
          submenu: [
            {label: 'Undo',         accelerator: this.isMac ? 'meta+z' : 'ctrl+z',              role: 'undo',           active: this.toPrevStepHistory },
            {label: 'Redo',         accelerator: this.isMac ? 'meta+shift+z' : 'ctrl+y',  role: 'redo',           active: this.toNextStepHistory },
            {type:  'separator'},
            {label: 'Copy',         accelerator: this.isMac ? 'meta+c' : 'ctrl+c',              role: 'copy',           active: this.HCCopy },
            {label: 'Paste',        accelerator: this.isMac ? 'meta+v' : 'ctrl+v',              role: 'paste',          active: this.HCPaste },
            {type:  'separator'},
            {label: 'Select all',   accelerator: this.isMac ? 'meta+a' : 'ctrl+a',              role: 'selectAll',      active: this.HCSelectAll },
            {label: 'Deselect all', accelerator: this.isMac ? 'meta+shift+a' : 'ctrl+shift+a',  enabled: this.openApp,  active: this.HCDeselectAll },

          ]
        },
        {
          label: 'Settings', visible: true,
          submenu: [
            {label: 'Edit profile',    enabled: false,         active: function() {} },
            {label: 'History',         enabled: false,         active: function() {} },
          ]
        },
        {
          role: 'window',
          label: 'Window', visible: true,
          submenu: [
            ...(this.isMac
              ? [
                  { role: 'minimize', active: ()=>{}},
                  { role: 'zoom',     active: ()=>{}},
                  { type: 'separator'},
                  { role: 'front',    active: ()=>{} },
                  { type: 'separator'},
                ]
              : [
                  {label: 'Minimize', active: this.appMinimize },
                  {label: 'Zoom',     active: this.appMaximize },
                ]
            ),
          ]
        },
        {
          role: 'help',
          label: 'Help', visible: true,
          submenu: [
            {label: 'Help',          enabled: false,                                  active: this.goToHelpPageDesktop },
            {label: 'About',                                                          active: this.goToAboutPageDesktop },
            ...(this.isMac
              ? []
              : [{label: 'Check for updates',                                         active: this.checkUpdate }]
            ),
            {type: 'separator'},
            {label: `Version: ${this.appVersion}`, enabled: false,                    active: ()=>{} }
          ]
        },
        {
          label: '', visible: false,
          submenu: [
            {type:  'separator'},
            {label: 'Delete',       accelerator: this.isMac ? 'meta+backspace' : 'delete',                              active: this.HC_delete,                    visible: false  },
            {label: 'DeleteMac',    accelerator: this.isMac ? 'backspace' : '',                              active: this.HC_delete,                    visible: false  },
            {label: 'Add group',    accelerator: this.isMac ? 'meta+g' : 'ctrl+g',              enabled: this.openApp,  active: this.HC_addLayerContainer,         visible: false  },
            {label: 'Ungroup',      accelerator: this.isMac ? 'meta+shift+g' : 'ctrl+shift+g',  enabled: this.openApp,  active: this.HC_unGroupLayerContainer,     visible: false  },
            {type:  'separator'},
            {label: 'Close setting popups',          accelerator: 'esc',                                                active: this.HC_esc,                       visible: false  },
          ]
        }
      ]
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
            {label: 'Save',         accelerator: this.isMac ? 'meta+s' : 'ctrl+s',              enabled: this.openApp && !this.isNotebookMode,  active: this.saveModel },
            {label: 'Save as',   accelerator: this.isMac ? 'meta+shift+s' : 'ctrl+shift+s',     enabled: this.openApp && !this.isNotebookMode,  active: this.saveModelAs },
            {type: 'separator'},
            {label: 'Export',  active: this.exportModel,        enabled: this.openApp},
            {label: 'Export to GitHub',  active: this.exportModelToGithub,        enabled: this.openApp},
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
            {label: 'Paste',        accelerator: this.isMac ? 'meta+v' : 'ctrl+v',              role: 'paste',      enabled: this.openApp,        active: this.HCPaste },

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
            {type: 'separator'},
            {label: `Version: ${this.appVersion}`, enabled: false,                    active: ()=>{} }
          ]
        },
        {
          label: '', visible: false,
          submenu: [
            {type:  'separator'},
            {label: 'Delete',       accelerator: this.isMac ? 'meta+backspace' : 'delete',                              active: this.HC_delete,                    visible: false  },
            {label: 'DeleteMac',    accelerator: this.isMac ? 'backspace' : '',                              active: this.HC_delete,                    visible: false  },
            {label: 'Add group',    accelerator: this.isMac ? 'meta+g' : 'ctrl+g',              enabled: this.openApp,  active: this.HC_addLayerContainer,         visible: false  },
            {label: 'Ungroup',      accelerator: this.isMac ? 'meta+shift+g' : 'ctrl+shift+g',  enabled: this.openApp,  active: this.HC_unGroupLayerContainer,     visible: false  },
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
      background: #124368;
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
