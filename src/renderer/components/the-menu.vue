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
            @click="subItem.active()"
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
      menuSet: false,

    }
  },
  mounted() {
    ipcRenderer.send('appVersion');
    ipcRenderer.on('getAppVersion', (event, data) => {
      this.appVersion = data;
    });
  },
  computed: {
    navMenu() {
      return [
        {
          label: 'File',
          submenu: [
            {label: 'New',                  enabled: this.menuSet,  active: ()=> {this.addNewNetwork()}},
            {label: 'Open trained model',   enabled: false,         active: ()=> {}},
            {label: 'Save trained model',   enabled: false,         active: ()=> {}},
            {label: 'Open untrained model', enabled: this.menuSet,  active: ()=> {this.openNetwork()}},
            {label: 'Save untrained model', enabled: this.menuSet,  active: ()=> {this.saveNetwork()}},
            {type: 'separator'},
            {label: 'Log out',              enabled: this.menuSet,  active: ()=> {this.logOut()}},
            {label: 'Quit',                 enabled: true,          active: ()=> {this.appClose()}}
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
            {label: 'delete',    enabled: false},
            {label: 'selectall', enabled: false},
          ]
        },
        {
          label: 'Settings',
          submenu: [
            {label: 'Hyperparameters', enabled: false, active: ()=> {this.appClose()}},
          ]
        },
        {
          label: 'Help',
          submenu: [
            {label: 'Help',                                     active: ()=> {this.openLink('https://www.perceptilabs.com/html/product.html#tutorials')}},
            {label: 'About',                                    active: ()=> {this.openLink('https://www.perceptilabs.com/')}},
            {label: 'Check for updates', enabled: this.menuSet, active: ()=> {this.checkUpdate()}},
            {type: 'separator'},
          ]
        }
      ]
    }
  },
  watch: {
    '$route': {
      handler(to, from) {
        to.name === 'app' ? this.menuSet = true : this.menuSet = false
      },
      immediate: true
    }
  },
  methods: {
    openLink(url) {
      window.open(url,'_blank');
    },
    appClose() {
      this.$store.dispatch('mod_events/EVENT_closeCore');
    },
    checkUpdate() {
      ipcRenderer.send('checkUpdate')
    },
    addNewNetwork() {
      this.$store.commit('mod_workspace/ADD_network');
    },
    openNetwork() {
      this.$store.commit('mod_events/set_openNetwork')
    },
    saveNetwork() {
      this.$store.commit('mod_events/set_saveNetwork')
    },
    logOut() {
      this.$router.replace({name: 'login'});
      this.$store.dispatch('mod_api/API_CLOSE_core', null, {root: true});
      this.$store.commit('mod_workspace/RESET_network');
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
