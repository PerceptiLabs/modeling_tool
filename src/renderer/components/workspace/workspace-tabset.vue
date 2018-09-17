<template lang="pug">
  .workspace_tabset
    ul.workspace_tab-list
      li.workspace_tab
        button.btn.btn--icon.tab_close(type="button") x
        span.tab_name Network_1
    .toggle-sidebar(:class="{'hide-sidebar': !hideSidebar}")
      button.btn.btn--icon(type="button" @click="toggleSidebar()")
        i.icon.icon-hide-right

</template>

<script>
export default {
  name: 'WorkspaceTabset',
  computed: {
    hideSidebar () {
      return this.$store.state.globalView.hideSidebar
    }
  },
  methods: {
    toggleSidebar () {
      this.$store.commit('globalView/SET_hideSidebar', !this.hideSidebar)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .workspace_tabset {
    padding-top: 2px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .workspace_tab-list {
    padding: 0 0 0 1em;
    margin: 0;
    list-style: none;
  }
  .workspace_tab {
    background-color: #23252A;
    border-radius: 10px 10px 0 0;
    min-width: 167px;
  }
  .tab_close {

  }
  .tab_name {

  }
  .toggle-sidebar {
    .btn {
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #4D556A;
      border-radius: 0;
    }
    .icon {
      @include multi-transition(transform)
    }
    &.hide-sidebar {
      .btn .icon{
        transform: rotateY(180deg);
      }
    }
  }
</style>
