<template lang="pug">
  nav.app-header_nav(v-if="showMenu")
    ul.header-nav
      li.header-nav_item(
      v-for="(item, i) in navMenu"
      :key="i"
      )
        button.btn.btn--link.header-nav_btn(type="button") {{ item.label }}
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
  import { ipcRenderer, shell } from 'electron'
  import { mapGetters, mapMutations, mapActions } from 'vuex';

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
  // data() {
  //   return {
  //     menuSet: false,
  //   }
  // },
  computed: {
    ...mapGetters({
      isTutorialMode:     'mod_tutorials/getIstutorialMode'
    }),
    appVersion() {
      return this.$store.state.globalView.appVersion
    },
    isOpenStoryBoard() {
      return this.$store.state.mod_tutorials.showTutorialStoryBoard
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
          label: 'File',
          submenu: [
            {label: 'Home',                                     enabled: this.openApp,  id: "to-home",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'New',        accelerator: 'Ctrl+N',        enabled: this.isLogin,  id: "net-new",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Open',       accelerator: 'Ctrl+O',        enabled: this.isLogin,  id: "net-open",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Save',       accelerator: 'Ctrl+S',        enabled: this.openApp,  id: "save",             active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Save as...', accelerator: 'Ctrl+Shift+S',  enabled: this.openApp,  id: "save-as",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: 'Log out',    accelerator: 'Ctrl+F4',       enabled: this.isLogin,  id: "log-out",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Exit',       accelerator: 'Ctrl+Q',        enabled: true,          id: "exit-app",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}}
          ]
        },
        {
          label: 'Edit',
          submenu: [
            {label: 'Undo',         accelerator: 'Ctrl+Z',      enabled: false,         id: "undo",             active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Redo',         accelerator: 'Ctrl+Shift+Z',enabled: false,         id: "redo",             active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: 'Copy',         accelerator: 'Ctrl+C',      enabled: this.openApp,  id: "copy",             active: function() {},                                mousedown: function() {ctx.menuEventSwitcher(this.id)}},
            {label: 'Paste',        accelerator: 'Ctrl+V',      enabled: this.openApp,  id: "paste",            active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: 'Select all',   accelerator: 'Ctrl+A',      enabled: this.openApp,  id: "select-all",       active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Deselect all', accelerator: 'Ctrl+Shift+A',enabled: this.openApp,  id: "deselect-all",     active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
          ]
        },
        {
          label: 'Window',
          submenu: [
              {label: 'Minimize',                               enabled: true,          id: "win-minimize",     active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
              {label: 'Zoom',                                   enabled: true,          id: "win-zoom",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
          ]
        },
        {
          label: 'Settings',
          submenu: [
            {label: 'Hyperparameters',                          enabled: this.openApp,  id: "open-net-param",   active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Edit profile',                             enabled: false,         id: "edit-profile",     active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'History',                                  enabled: false,         id: "history",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
          ]
        },
        {
          label: 'Help',
          submenu: [
            {label: 'Help',                                                             id: "to-help",          active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'About',                                                            id: "to-about",         active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Tutorial mode',                   enabled: !this.isOpenStoryBoard, id: "enable-tutorial",  active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {label: 'Check for updates',                                                id: "check-updates",    active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {type: 'separator'},
            {label: `Version: ${this.appVersion}`,               enabled: false,}
          ]
        },
        {
          label: '',
          visible: false,
          submenu: [
            {visible: false, label: 'Delete', accelerator: this.isMac ? 'backspace+meta' : 'delete',    id: "hc-delete", active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {visible: false, label: 'addLayerContainer', accelerator: 'Ctrl+G', enabled: this.openApp,  id: "hc-add-layer-container",    active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
            {visible: false, label: 'unGroupLayerContainer', accelerator: 'Ctrl+Shift+G', enabled: this.openApp, id: "hc-ungroup-container", active: function() {ctx.menuEventSwitcher(this.id)},  mousedown: ()=> {}},
          ]
        }
      ]
    }
  },
  watch: {
    navMenu(newMenu) {
      ipcRenderer.send('app-menu', newMenu)
      //ipcRenderer.send('app-menu', JSON.parse(JSON.stringify(newMenu)))


      // if(process.platform === 'darwin') {
      // }
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
      appClose:         'mod_events/EVENT_closeApp',
      HCCopy:           'mod_events/EVENT_hotKeyCopy',
      HCPaste:          'mod_events/EVENT_hotKeyPaste',
      HCSelectAll:      'mod_workspace/SET_elementSelectAll',
      HCDeselectAll:    'mod_workspace/SET_elementUnselect'
    }),
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
          this.openLink('https://www.perceptilabs.com/html/product.html#tutorials');
          break;
        case 'to-about':
          this.openLink('https://www.perceptilabs.com/');
          break;
        case 'enable-tutorial':
          this.showTutorial();
          break;
        case 'check-updates':
          this.checkUpdate();
          break;
        //Hot keys
        case 'hc-delete':

          break;
        case 'hc-add-layer-container':

          break;
        case 'hc-ungroup-container':

          break;
      }
    },
    openLink(url) {
      shell.openExternal(url);
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
    appMinimize() {
      ipcRenderer.send('app-minimize')
    },
    appMaximize() {
      ipcRenderer.send('app-maximize')
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
