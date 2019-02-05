<template lang="pug">
  nav.app-header_nav
    ul.header-nav
      li(
      v-for="(item, i) in navMenu"
      :key="i"
      )
        button.btn.btn--link(type="button") {{ item.label }}
        ul.header-nav_sublist.show-hide.sublist--top
          li(
            v-for="(subItem, index) in item.submenu"
            :key="index"
            :class="{'have-sublist' : subItem.submenu}"
          )
            div.separator(v-if="subItem.type === 'separator'")
            button.btn.btn--link(type="button" v-else
              :disabled="subItem.enabled === false"
              @click="subItem.active()"
            ) {{subItem.label}}
              i.icon.icon-shevron-right(v-if="subItem.submenu")
            div.btn(v-if="i === navMenu.length - 1 && index === item.submenu.length - 1") Version: {{appVersion}}
            ul.header-nav_sublist.sublist--right
              li(
                v-for="(subSubItem, index) in subItem.submenu"
              )
                button.btn.btn--link(type="button"
                  :disabled="subSubItem.enabled === false"
                  @click="subItem.active()"
                ) {{subSubItem.label}}

</template>

<script>
  import {ipcRenderer} from 'electron'
export default {
  name: "TheMenu",
  data() {
    return {
      menuSet: false,
    }
  },
  computed: {
    appVersion() {
      return this.$store.state.globalView.appVersion
    },
    userIsLogin() {
      return this.$store.getters['globalView/GET_userIsLogin']
    },
    navMenu() {
      return [
        {
          label: 'File',
          submenu: [
            {label: 'New project',                  enabled: this.menuSet,  active: ()=> {this.addNewNetwork()}},
            {label: 'New workspace',                enabled: false,         active: ()=> {}},
            {label: 'Open project',                 enabled: this.menuSet,  active: ()=> {this.openProject()}},
            {label: 'Save project',                 enabled: false,         active: ()=> {this.saveProject()}},
            {label: 'Open model',                   enabled: this.menuSet,  active: ()=> {this.openNetwork()}},
            {label: 'Save model',                   enabled: this.menuSet,  active: ()=> {this.saveNetwork()}},
            {type: 'separator'},
            {label: 'Log out',                      enabled: this.menuSet,  active: ()=> {this.logOut()}},
            {label: 'Exit',                         enabled: true,          active: ()=> {this.appClose()}}
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
          ]
        },
        {
          label: 'Custom'
        },
        {
          label: 'Window',
          submenu: [
            {label: 'Edit profile',                 enabled: false, active: ()=> {this.appClose()}},
            {label: 'History',                      enabled: false, active: ()=> {this.appClose()}},
          ]
        },
        {
          label: 'Settings',
          submenu: [
            {label: 'Hyperparameters',              enabled: false, active: ()=> {this.appClose()}},
          ]
        },
        {
          label: 'Help',
          submenu: [
            {label: 'Help',                                                 active: ()=> {this.openLink('https://www.perceptilabs.com/html/product.html#tutorials')}},
            {label: 'About',                                                active: ()=> {this.openLink('https://www.perceptilabs.com/')}},
            {label: 'Tutorial mode',                enabled: this.menuSet,  active: ()=> {}},
            {label: 'Check for updates',                                    active: ()=> {this.checkUpdate()}},
            {type: 'separator'},
          ]
        }
      ]
    }
  },
  watch: {
    userIsLogin: {
      handler(to, from) {
        to ? this.menuSet = true : this.menuSet = false
      },
      immediate: true
    },
    eventLogout() {
      this.logOut()
    }
  },
  methods: {
    openLink(url) {
      window.open(url,'_blank');
    },
    appClose() {
      this.$store.dispatch('mod_events/EVENT_closeApp');
    },
    checkUpdate() {
      ipcRenderer.send('checkUpdate', 'userCheck');
    },
    addNewNetwork() {
      this.$store.dispatch('mod_workspace/ADD_network');
      if(this.$router.history.current.name !== 'app') {
        this.$router.replace({name: 'app'});
      }
    },
    openNetwork() {
      this.$store.commit('mod_events/set_openNetwork')
    },
    openProject() {
      this.$router.replace({name: 'projects'});
    },
    saveNetwork() {
      if(this.$router.history.current.name !== 'app') {
        return
      }
      this.$store.commit('mod_events/set_saveNetwork');
    },
    saveProject() {

    },
    logOut() {
      this.$store.dispatch('mod_events/EVENT_logOut')
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
    > li {
      font-size: 14px;
      color: $col-txt;
      position: relative;
      display: flex;
      align-items: center;
      &:hover {
        background: $disable-txt;
      }
    }
    > li + li {
      //margin-left: 2rem;
    }
    .btn {
      padding: 0 1rem;
      -webkit-app-region: no-drag;
    }
  }
  .header-nav_sublist {
    font-weight: 400;
    position: absolute;
    z-index: 1;
    min-width: 10rem;
    background-color: $bg-workspace;
    box-shadow: $box-shad;
    &.sublist--top {
      top: 100%;
    }
    &.sublist--right {
      top: 0;
      left: 100%;
    }
    li {
      color: $white;
      position: relative;
    }
    .open-sublist &,
    .header-nav li:hover &.show-hide {
      display: block;
    }
    .btn {
      width: 100%;
      padding: .7rem 9rem .7rem 2rem;
      text-align: left;
      white-space: nowrap;
      border-radius: 0;
      &:hover {
        background: #124368;
      }
    }
    .separator {
      height: 1px;
      margin: .25rem 2px;
      background: #141419;
    }
    .have-sublist {
      .icon-shevron-right{
        position: absolute;
        right: 1rem;
      }
      ul {
        display: none;
      }
    }
    .have-sublist:hover ul {
      display: block;
    }
  }
  .show-hide {
    display: none;
  }
</style>
