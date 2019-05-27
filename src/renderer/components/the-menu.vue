<template lang="pug">
  nav.app-header_nav
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
              @click="subItem.active()"
            )
              span.header-nav_btn-text {{ subItem.label }}
              span.text-disable(
                v-if="subItem.accelerator"
                ) {{ subItem.accelerator }}
              i.icon.icon-shevron-right(
                v-if="subItem.submenu"
                )
            div.header-nav_sublist-btn(
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
  import {ipcRenderer, shell} from 'electron'
  import { mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: "TheMenu",
  data() {
    return {
      menuSet: false,

    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:     'mod_tutorials/getIstutorialMode'
    }),
    appVersion() {
      return this.$store.state.globalView.appVersion
    },
    openApp() {
      return this.$store.state.globalView.appIsOpen
    },
    isLogin() {
      return this.$store.state.globalView.userToken ? true : false
    },
    navMenu() {
      return [
        {
          label: 'File',
          submenu: [
            {label: 'Home',                                     enabled: this.openApp,  active: ()=> {this.openProject()}},
            {label: 'New',        accelerator: 'Ctrl+N',        enabled: this.isLogin,  active: ()=> {this.addNewNetwork()}},
            {label: 'Open',       accelerator: 'Ctrl+O',        enabled: this.isLogin,  active: ()=> {this.openNetwork()}},
            {label: 'Save',       accelerator: 'Ctrl+S',        enabled: this.openApp,  active: ()=> {this.saveNetwork()}},
            {label: 'Save as...', accelerator: 'Ctrl+Shift+S',  enabled: this.openApp,  active: ()=> {this.saveNetworkAs()}},
            {type: 'separator'},
            {label: 'Log out',    accelerator: 'Ctrl+F4',       enabled: this.isLogin,  active: ()=> {this.logOut()}},
            {label: 'Exit',       accelerator: 'ALT+F4',        enabled: true,          active: ()=> {this.appClose()}}
          ]
        },
        {
          label: 'Edit',
          submenu: [
            {label: 'Undo',                         enabled: false},
            {label: 'Redo',                         enabled: false},
            {type: 'separator'},
            {label: 'Cut',                          enabled: false},
            {label: 'Copy',                         enabled: false},
            {label: 'Paste',                        enabled: false},
            {label: 'Delete',                       enabled: false},
            {label: 'Select all',                   enabled: false},
          ]
        },
        {
          label: 'Operations ',
          submenu: [
            {
              label: 'Data',
              submenu: [
                {label: 'Data',                     enabled: false,    active: ()=> {}},
                {label: 'Data Environment',         enabled: false,    active: ()=> {}},
              ]
            },
            {
              label: 'Process ',
              submenu: [
                {label: 'Reshape',                  enabled: false,    active: ()=> {}},
                {label: 'Word embedding',           enabled: false,    active: ()=> {}},
                {label: 'Grayscale',                enabled: false,    active: ()=> {}},
                {label: 'One hot',                  enabled: false,    active: ()=> {}},
                {label: 'Crop',                     enabled: false,    active: ()=> {}},
              ]
            },
            {
              label: 'Deep learning',
              submenu: [
                {label: 'Fully connected',          enabled: false,    active: ()=> {}},
                {label: 'Convolution',              enabled: false,    active: ()=> {}},
                {label: 'Deconvolution',            enabled: false,    active: ()=> {}},
                {label: 'Recurrent',                enabled: false,    active: ()=> {}}
              ]
            },
            {
              label: 'Math',
              submenu: [
                {label: 'Argmax',                   enabled: false,    active: ()=> {}},
                {label: 'Merge',                    enabled: false,    active: ()=> {}},
                {label: 'Split',                    enabled: false,    active: ()=> {}},
                {label: 'Softmax',                  enabled: false,    active: ()=> {}}
              ]
            },
            {
              label: 'Training',
              submenu: [
                {label: 'Normal',                   enabled: false,    active: ()=> {}},
                {label: 'Normal+Data',              enabled: false,    active: ()=> {}},
                {label: 'Reinforcement learning',   enabled: false,    active: ()=> {}},
                {label: 'Genetic algorithm',        enabled: false,    active: ()=> {}},
                {label: 'Dynamic routing',          enabled: false,    active: ()=> {}}
              ]
            },
            {
              label: 'Classic machine learning',
              submenu: [
                {label: 'K means clustering',       enabled: false,    active: ()=> {}},
                {label: 'DBSCAN',                   enabled: false,    active: ()=> {}},
                {label: 'kNN',                      enabled: false,    active: ()=> {}},
                {label: 'Random forrest',           enabled: false,    active: ()=> {}},
                {label: 'Support vector machine',   enabled: false,    active: ()=> {}}
              ]
            },
            {
              label: 'Custom'
            },
          ]
        },
        {
          label: 'Window',
          submenu: [
            {label: 'Edit profile',                 enabled: false, active: ()=> {}},
            {label: 'History',                      enabled: false, active: ()=> {}},
          ]
        },
        {
          label: 'Settings',
          submenu: [
            {label: 'Hyperparameters',              enabled: false, active: ()=> {}},
          ]
        },
        {
          label: 'Help',
          submenu: [
            {label: 'Help',                                                 active: ()=> {this.openLink('https://www.perceptilabs.com/html/product.html#tutorials')}},
            {label: 'About',                                                active: ()=> {this.openLink('https://www.perceptilabs.com/')}},
            {label: 'Tutorial mode',                enabled: this.openApp,  active: ()=> {this.showTutorial()}},
            {label: 'Check for updates',                                    active: ()=> {this.checkUpdate()}},
            {type: 'separator'},
          ]
        }
      ]
    }
  },
  methods: {
    ...mapMutations({
      setTutorialSB: 'mod_tutorials/SET_showTutorialStoryBoard',
      openNetwork:   'mod_events/set_openNetwork',
      saveNetwork:   'mod_events/set_saveNetwork',
      saveNetworkAs: 'mod_events/set_saveNetworkAs',
    }),
    ...mapActions({
      infoPopup:     'globalView/GP_infoPopup',
      appClose:      'mod_events/EVENT_closeApp',
    }),
    openLink(url) {
      shell.openExternal(url);
    },
    checkUpdate() {
      ipcRenderer.send('checkUpdate', 'userCheck');
    },
    addNewNetwork() {
      this.$store.dispatch('mod_workspace/ADD_network', {'ctx': this});
    },
    openProject() {
      this.$router.replace({name: 'projects'});
    },
    logOut() {
      this.$store.dispatch('mod_events/EVENT_logOut', this)
    },
    showTutorial() {
      this.isTutorialMode ? this.infoPopup('Tutorial mode is already enabled') : this.setTutorialSB(true);
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
