<template lang="pug">
  nav.app-header_nav(v-if="showMenu")
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
              @mousedown="subItem.mousedown()"
              @click="subItem.active()"
            )
              span.header-nav_btn-text {{ subItem.label }}
              span.text-disable(
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
                  @click="subSubItem.active()"
                )
                  span {{subSubItem.label}}
                  span.text-disable(
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
      default: true
    }
  },
  mounted() {
    this.electronMenuListener();
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
      return !!this.$store.state.globalView.userToken
    },
    isMac() {
      return process.platform === 'darwin'
    },
    navMenu() {
      const ctx = this;
      return [
        {
          label: 'File', visible: true,
          submenu: [
            {label: 'Home',                                                                       enabled: this.openApp,  id: "to-home",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'New',          accelerator: this.isMac ? 'Command+N' : 'Ctrl+N',             enabled: this.isLogin,  id: "net-new",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Open',         accelerator: this.isMac ? 'Command+O' : 'Ctrl+O',             enabled: this.isLogin,  id: "net-open",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Save',         accelerator: this.isMac ? 'Command+S' : 'Ctrl+S',             enabled: this.openApp,  id: "save",             active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Save as...',   accelerator: this.isMac ? 'Command+Shift+S' : 'Ctrl+Shift+S', enabled: this.openApp,  id: "save-as",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: 'Log out',                                                                    enabled: this.isLogin,  id: "log-out",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Exit',         accelerator: this.isMac ? 'Command+N' : 'Ctrl+Q',             enabled: true,          id: "exit-app",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}}
          ]
        },
        {
          label: 'Edit', visible: true,
          submenu: [
            {label: 'Undo',         accelerator: this.isMac ? 'Command+Z' : 'Ctrl+Z',             enabled: false,         id: "undo",             active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Redo',         accelerator: this.isMac ? 'Command+Shift+Z' : 'Ctrl+Shift+Z', enabled: false,         id: "redo",             active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: 'Copy',         accelerator: this.isMac ? 'Command+C' : 'Ctrl+C',             enabled: this.openApp,  id: "copy",             active: function() {},                                mousedown: function() {ctx.menuEventSwitcher(this.id)}},
            {label: 'Paste',        accelerator: this.isMac ? 'Command+V' : 'Ctrl+V',             enabled: this.openApp,  id: "paste",            active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: 'Select all',   accelerator: this.isMac ? 'Command+A' : 'Ctrl+A',             enabled: this.openApp,  id: "select-all",       active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Deselect all', accelerator: this.isMac ? 'Command+Shift+A' : 'Ctrl+Shift+A', enabled: this.openApp,  id: "deselect-all",     active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
          ]
        },
        {
          label: 'Window', visible: true,
          submenu: [
              {label: 'Minimize',                                                                 enabled: true,          id: "win-minimize",     active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
              {label: 'Zoom',                                                                     enabled: true,          id: "win-zoom",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
          ]
        },
        {
          label: 'Settings', visible: true,
          submenu: [
            {label: 'Hyperparameters',                                                            enabled: this.openApp,  id: "open-net-param",   active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Edit profile',                                                               enabled: false,         id: "edit-profile",     active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'History',                                                                    enabled: false,         id: "history",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
          ]
        },
        {
          label: 'Help', visible: true,
          submenu: [
            {label: 'Help',                                                                                               id: "to-help",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'About',                                                                                              id: "to-about",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Tutorial mode',                                                     enabled: !this.isTutorialActive && this.isLogin, id: "enable-tutorial",  active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Check for updates',                                                                                  id: "check-updates",    active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: `Version: ${this.appVersion}`,                                                enabled: false,}
          ]
        },
        {
          label: '', visible: false,
          submenu: [
            {label: 'Delete',                accelerator: this.isMac ? 'backspace+meta' : 'delete',                                 id: "hc-delete",              active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}, visible: false},
            {label: 'Esc',                   accelerator: 'esc',                                                                    id: "hc-esc",                 active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}, visible: false},
            {label: 'addLayerContainer',     accelerator: this.isMac ? 'Command+G' : 'Ctrl+G',              enabled: this.openApp,  id: "hc-add-layer-container", active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}, visible: false},
            {label: 'unGroupLayerContainer', accelerator: this.isMac ? 'Command+Shift+G' : 'Ctrl+Shift+G',  enabled: this.openApp,  id: "hc-ungroup-container",   active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}, visible: false},
            {label: 'preventClose',          accelerator: 'Alt+F4',                                         enabled: true,          id: "hc-prevent-close",       active: function(e) {e.preventDefault()},             mousedown: ()=> {}, visible: false},
          ]
        }
      ]
    }
  },
  watch: {
    navMenu(newMenu) {
      ipcRenderer.send('app-menu', newMenu)
    }
  },
  methods: {
    ...mapMutations({
      setTutorialSB:    'mod_tutorials/SET_showTutorialStoryBoard',
      openNetwork:      'mod_events/set_openNetwork',
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
      HCCopy:           'mod_events/EVENT_hotKeyCopy',
      HCPaste:          'mod_events/EVENT_hotKeyPaste',
      HCSelectAll:      'mod_workspace/SET_elementSelectAll',
      HCDeselectAll:    'mod_workspace/SET_elementUnselect'
    }),
    goToLink,
    electronMenuListener() {
      ipcRenderer.on('menu-event', (event, menuId) => {
        this.menuEventSwitcher(menuId)
      });
    },
    menuEventSwitcher(menuId) {
      switch (menuId) {
        //File
        case 'to-home':
          this.openProject();
          break;
        case 'net-new':
          this.addNewNetwork();
          break;
        case 'net-open':
          this.openModel();
          break;
        case 'save':
          this.saveModel();
          break;
        case 'save-as':
          this.saveModelAs();
          break;
        case 'log-out':
          this.logOut();
          break;
        case 'exit-app':
          this.appClose();
          break;
        //Edit
        case 'undo':

          break;
        case 'redo':

          break;
        case 'copy':
          this.HCCopy();
          break;
        case 'paste':
          this.HCPaste();
          break;
        case 'select-all':
          this.HCSelectAll();
          break;
        case 'deselect-all':
          this.HCDeselectAll();
          break;
        //Window
        case 'win-minimize':
          this.appMinimize();
          break;
        case 'win-zoom':
          this.appMaximize();
          break;
        //Settings
        case 'open-net-param':
          this.openHyperparameters();
          break;
        case 'edit-profile':

          break;
        case 'history':

          break;
        //Help
        case 'to-help':
          this.goToLink(`${baseUrlSite}/i_docs`);
          break;
        case 'to-about':
          this.goToLink(`${baseUrlSite}/about`);
          break;
        case 'enable-tutorial':
          this.showTutorial();
          break;
        case 'check-updates':
          this.checkUpdate();
          break;
        //Hot keys
        case 'hc-delete':
          this.HC_delete();
          break;
        case 'hc-esc':
          this.HC_esc();
          break;
        case 'hc-add-layer-container':
          this.HC_addLayerContainer();
          break;
        case 'hc-ungroup-container':
          this.HC_unGroupLayerContainer();
          break;
      }
    },
    checkUpdate() {
      this.$store.commit('mod_autoUpdate/SET_showNotAvailable', true);
      ipcRenderer.send('check-update');
    },
    addNewNetwork() {
      this.$store.dispatch('mod_workspace/ADD_network', {'ctx': this});
      this.offMainTutorial();
    },
    openProject() {
      this.$router.replace({name: 'projects'});
      this.offMainTutorial();
    },
    logOut() {
      this.$store.dispatch('mod_events/EVENT_logOut', this);
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
</style>
