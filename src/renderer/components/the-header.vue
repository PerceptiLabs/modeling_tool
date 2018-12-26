<template lang="pug">
  header.app-header
    .app-header_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    nav.app-header_nav
      ul.header-nav
        li(
          v-for="(item, i) in navMenu"
          :key="i"
          )
          button.btn.btn--link(type="button") {{ item.label }}
          ul.header-nav_sublist
            li(
              v-for="(subItem, i) in item.subMenu"
              :key="subItem.id")
              div.separator(v-if="subItem.type === 'separator'")
              button.btn.btn--link(type="button" v-else
              ) {{subItem.label}}

    ul.app-header_actions
      button.btn.btn--app-minify(type="button").i.icon.icon-minus
      button.btn.btn--app-full(type="button").i.icon.icon-full-screen
      button.btn.btn--app-close(type="button").i.icon.icon-close
</template>

<script>
export default {
    name: "TheHeader",
    data() {
        return {
          navMenu: [
            {
              label: 'File',
              subMenu: [
                { label: 'New',                 enabled: true,  action: 'action' },
                { label: 'Open trained model',  enabled: false, action: 'action' }
              ]
            },
            {
              label: 'Edit',
              subMenu: [
                { label: 'Undo',  enabled: false,  action: 'action' },
                { label: 'Redo',  enabled: false, action: 'action' },
                { type: 'separator' },
                { label: 'Undo',  enabled: false,  action: 'action' },
                { label: 'Redo',  enabled: false, action: 'action' },
              ]
            }
          ]
        }
    },
    methods: {

    }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  $headerHeight: 3rem;
  .app-header {
    background: #141419;
    display: flex;
    align-items: center;
    height: $headerHeight;
    -webkit-app-region: drag;
    .btn {
      -webkit-app-region: no-drag;
    }
  }
  .app-header_logo {
    padding-left: 2rem;
    padding-right: 2rem;
    img {
      height: $headerHeight - 1;
    }
  }
  .header-nav {
    display: flex;
    font-weight: 500;
    > li {
      position: relative;
    }
    > li + li {
      margin-left: 2rem;
    }
  }
  .header-nav_sublist {
    display: none;
    position: absolute;
    top: 100%;
    left: -1rem;
    min-width: 10rem;
    box-shadow: $box-shad;
    padding: .5rem 0;
    background-color: $bg-input;
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
  .app-header_actions {
    margin-left: auto;
    display: flex;
    .btn {
      height: $headerHeight;
      width: $headerHeight * 2;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5em;
      border-radius: 0;
      &:hover {
        background: $bg-grad-disable;
      }
    }
    .btn--app-minify {

    }
    .btn--app-full {

    }
    .btn--app-close {
      &:hover {
        background: $col-error;
      }
    }
  }
</style>
