<template lang="pug">
  ul.header-nav
    li(
    v-for="(item, i) in navMenu"
    :key="i"
    )
      button.btn.btn--link(type="button") {{ item.label }}
      ul.header-nav_sublist
        li(
        v-for="(subItem, index) in item.submenu"
        :key="index")
          div.separator(v-if="subItem.type === 'separator'")
          button.btn.btn--link(type="button" v-else
            :disabled="subItem.enabled === false"
            @click="subItem.active(ctx)"
          ) {{subItem.label}}
          div.btn(v-if="i === navMenu.length - 1 && index === item.submenu.length - 1") Version: {{appVersion}}

</template>

<script>
  import {ipcRenderer} from 'electron'
export default {
  name: "TheMenu",
  data() {
    return {
      appVersion: '',
      ctx: this,
      navMenu: [
        {
          label: 'File',
          submenu: [
            {label: 'New',                                    active: function(self) {self.addNewNetwork()} },
            {label: 'Open trained model',   enabled: false,   active: function(self) {}},
            {label: 'Save trained model',   enabled: false,   active: function(self) {}},
            {label: 'Open untrained model',                   active: function(self) {self.openNetwork()}},
            {label: 'Save untrained model',                   active: function(self) {self.saveNetwork()}},
            {type: 'separator'},
            {label: 'Quit',                                   active: function(self) {self.appClose()}}
          ]
        },
        {
          label: 'Edit',
          submenu: [
            {label: 'undo',      enabled: false},
            {label: 'redo',      enabled: false},
            {type: 'separator'},
            {label: 'cut',       enabled: false},
            {label: 'copy',      enabled: false},
            {label: 'paste',     enabled: false},
            {label: 'delete',    accelerator: 'Delete', enabled: false},
            {label: 'selectall', enabled: false},
          ]
        },
        {
          label: 'Settings',
          submenu: [
            {label: 'Hyperparameters', enabled: false, active: function(self) {self.appClose()}},
          ]
        },
        {
          label: 'Help',
          submenu: [
            {label: 'Help',               active: function(self) {self.openLink('https://www.perceptilabs.com/html/product.html#tutorials')}},
            {label: 'About',              active: function(self) {self.openLink('https://www.perceptilabs.com/')}},
            {label: 'Check for updates',  active: function(self) {self.checkUpdate()}},
            {type: 'separator'},
          ]
        }
      ]
    }
  },
  mounted() {
    ipcRenderer.send('appVersion');
    ipcRenderer.on('getAppVersion', (event, data) => {
      this.appVersion = data;
    });
  },
  computed: {
    version() {

    }
  },
  methods: {
    openLink(url) {
      window.open(url,'_blank');
    },
    appClose() {
      ipcRenderer.send('appClose')
    },
    checkUpdate() {
      ipcRenderer.send('checkUpdate')
    },
    addNewNetwork() {
      this.$store.commit('mod_workspace/ADD_loadNetwork');
    },
    openNetwork() {
      this.$store.commit('mod_events/set_openNetwork')
    },
    saveNetwork() {
      this.$store.commit('mod_events/set_saveNetwork')
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .header-nav {
    display: flex;
    font-weight: 500;
    > li {
      position: relative;
    }
    > li + li {
      margin-left: 2rem;
    }
    .btn {
      -webkit-app-region: no-drag;
    }
  }
  .header-nav_sublist {
    display: none;
    position: absolute;
    top: 70%;
    left: -1rem;
    min-width: 10rem;
    box-shadow: $box-shad;
    padding: .5rem 0;
    background-color: $bg-input;
    z-index: 1;
    .open-sublist &,
    .header-nav li:hover & {
      display: block;
    }
    .btn {
      white-space: nowrap;
      padding: .25rem 1rem;
      &:hover {
        background: #000;
      }
    }
    .separator {
      margin: .25rem 2px;
      height: 1px;
      background: #141419;
    }
  }
</style>
