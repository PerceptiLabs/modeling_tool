<template lang="pug">
  nav.app-header_nav(v-if="showMenu" v-hotkey="keymap")
    ul.header-nav
      li.header-nav_item(
      v-for="(item, i) in navMenu"
      :key="i"
      )
        button.btn.btn--link.header-nav_btn(type="button"
          v-if="item.visible"
        ) {{ item.label }}
        ul.header-nav_sublist.sublist--top
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
            //-div.header-nav_sublist-btn(
              v-if="i === navMenu.length - 1 && index === item.submenu.length - 1"
              ) Version: {{appVersion}}
            ul.header-nav_sublist.sublist--right(v-if="subItem.submenu")
              li.header-nav_item(
                v-for="(subSubItem, ind) in subItem.submenu"
                :key="subSubItem.ind"
              )
                button.btn.btn--link.header-nav_sublist-btn(type="button"
                  :disabled="subSubItem.enabled === false"
                  @click="subItem.active ? subItem.active() : ()=>{}"
                )
                  span {{subSubItem.label}}
                  span.text-disable.hotkey(
                    v-if="subSubItem.accelerator"
                  ) {{ subSubItem.accelerator }}

</template>

<script>
  import { ipcRenderer } from 'electron'
  import { mapGetters, mapMutations, mapActions } from 'vuex';
  import { baseUrlSite } from '@/core/constants.js';
  import { goToLink }    from '@/core/helpers.js'

export default {
  name: "TheMenu",
  props: {
    showMenu: {
      type: Boolean,
      default: true,
    }
  },
  data() {
    return {
      dataKeymap: {}
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode: 'mod_tutorials/getIstutorialMode',
      isStoryBoard:   'mod_tutorials/getIsTutorialStoryBoard'
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
    isLogin() {
      return this.$store.getters['mod_user/GET_userIsLogin']
    },
    isMac() {
      return process.platform === 'darwin'
    },

    navMenu() {
      return [
        {
          label: 'File', visible: true,
          submenu: [
            {label: 'New',          accelerator: this.isMac ? 'meta+n' : 'ctrl+n',                        enabled: this.isLogin,        active: this.addNewNetwork },
            {label: 'Open',         accelerator: this.isMac ? 'meta+o' : 'ctrl+o',                        enabled: this.isLogin,        active: this.openModel },
            {label: 'Save',         accelerator: this.isMac ? 'meta+s' : 'ctrl+s',                        enabled: this.openApp,        active: this.saveModel },
            {label: 'Save as...',   accelerator: this.isMac ? 'meta+shift+S' : 'ctrl+shift+s',            enabled: this.openApp,        active: this.saveModelAs },
            {type: 'separator'},
            {label: 'Log out',                                                                            enabled: this.isLogin,        active: this.logOut },
            {label: 'Exit',         accelerator: this.isMac ? 'meta+q' : 'ctrl+q',                        enabled: true,                active: this.appClose }
          ]
        },
        {
          label: 'Edit', visible: true,
          submenu: [
            {label: 'Undo',         accelerator: this.isMac ? 'meta+z' : 'ctrl+z',                        enabled: false,               active: function() {} },
            {label: 'Redo',         accelerator: this.isMac ? 'meta+shift+z' : 'ctrl+shift+z',            enabled: false,               active: function() {} },
            {type: 'separator'},
            {label: 'Copy',         accelerator: this.isMac ? 'meta+c' : 'ctrl+c',                        enabled: this.openApp,        active: this.HCCopy },
            {label: 'Paste',        accelerator: this.isMac ? 'meta+v' : 'ctrl+v',                        enabled: this.openApp,        active: this.HCPaste },
            {type: 'separator'},
            {label: 'Select all',   accelerator: this.isMac ? 'meta+a' : 'ctrl+a',                        enabled: this.openApp,        active: this.HCSelectAll },
            {label: 'Deselect all', accelerator: this.isMac ? 'meta+shift+a' : 'ctrl+shift+a',            enabled: this.openApp,        active: this.HCDeselectAll },
          ]
        },
        {
          label: 'Window', visible: true,
          submenu: [
            {label: 'Minimize',                                                                           enabled: true,                active: this.appMinimize },
            {label: 'Zoom',                                                                               enabled: true,                active: this.appMaximize },
          ]
        },
        {
          label: 'Settings', visible: true,
          submenu: [
            {label: 'Hyperparameters',                                                                    enabled: this.openApp,        active: this.openHyperparameters },
            {label: 'Edit profile',                                                                       enabled: false,               active: function() {} },
            {label: 'History',                                                                            enabled: false,               active: function() {} },
          ]
        },
        {
          label: 'Help', visible: true,
          submenu: [
            {label: 'Help',                                                                                                             active: () => {this.goToLink(`${baseUrlSite}/i_docs`)} },
            {label: 'About',                                                                                                            active: () => {this.goToLink(`${baseUrlSite}/about`);} },
            {label: 'Tutorial mode',                                                                      enabled: !this.isTutorialActive && this.isLogin,     active: this.showTutorial },
            {label: 'Check for updates',                                                                                                active: this.checkUpdate },
            {type: 'separator'},
            {label: `Version: ${this.appVersion}`,                                                        enabled: false,}
          ]
        },
        {
          label: '', visible: false,
          submenu: [
            {label: 'Delete',                accelerator: this.isMac ? 'backspace+meta' : 'delete',                                      active: this.HC_delete,                    visible: false  },
            {label: 'Esc',                   accelerator: 'esc',                                                                         active: this.HC_esc,                       visible: false  },
            {label: 'addLayerContainer',     accelerator: this.isMac ? 'meta+g' : 'ctrl+g',               enabled: this.openApp,         active: this.HC_addLayerContainer,         visible: false  },
            {label: 'unGroupLayerContainer', accelerator: this.isMac ? 'meta+shift+g' : 'ctrl+shift+g',   enabled: this.openApp,         active: this.HC_unGroupLayerContainer,     visible: false  },
            {label: 'preventClose',                                                                       enabled: true,                 active: function(e) {e.preventDefault()},  visible: false  },
          ]
        }
      ]
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
  },
  watch: {
    navMenu(newMenu) {
      ipcRenderer.send('app-menu', newMenu)
    }
  },
  methods: {
    ...mapMutations({
      setTutorialSB:    'mod_tutorials/SET_showTutorialStoryBoard',
      saveNetwork:      'mod_events/set_saveNetwork',
      saveNetworkAs:    'mod_events/set_saveNetworkAs',
      setTutorialMode:  'mod_tutorials/SET_isTutorialMode',
    }),
    ...mapActions({
      infoPopup:        'globalView/GP_infoPopup',
      offMainTutorial:  'mod_tutorials/offTutorial',
      appClose:         'mod_events/EVENT_appClose',
      appMinimize:      'mod_events/EVENT_appMinimize',
      appMaximize:      'mod_events/EVENT_appMaximize',
      openNetwork:      'mod_events/EVENT_openNetwork',
      HCCopy:           'mod_events/EVENT_hotKeyCopy',
      HCPaste:          'mod_events/EVENT_hotKeyPaste',
      HCSelectAll:      'mod_workspace/SET_elementSelectAll',
      HCDeselectAll:    'mod_workspace/SET_elementUnselect'
    }),
    goToLink,
    checkUpdate() {
      this.$store.commit('mod_autoUpdate/SET_showNotAvailable', true);
      ipcRenderer.send('check-update');
    },
    addNewNetwork() {
      this.$store.dispatch('mod_workspace/ADD_network');
      this.offMainTutorial();
    },
    logOut() {
      this.$store.dispatch('mod_events/EVENT_logOut');
      this.offMainTutorial();
    },
    showTutorial() {
      this.$store.dispatch('mod_tutorials/START_storyboard');
    },
    openHyperparameters() {
      this.$store.commit('globalView/GP_showNetGlobalSet', true);
    },
    openModel() {
      this.openNetwork();
      this.offMainTutorial();
    },
    saveModel() {
      this.saveNetwork();
      this.offMainTutorial();
    },
    saveModelAs() {
      this.saveNetworkAs();
      this.offMainTutorial();
    },
    HC_delete() {
      if(!this.isTutorialMode) {
        this.$store.dispatch('mod_events/EVENT_hotKeyDeleteElement')
      }
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
  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .app-header_nav {
    height: 100%;
    -webkit-app-region: no-drag;
  }
  .header-nav {
    font-weight: 500;
    display: flex;
    height: 100%;
    > .header-nav_item {
      font-size: 14px;
      color: $col-txt;
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
