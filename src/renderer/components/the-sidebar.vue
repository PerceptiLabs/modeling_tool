<template lang="pug">
  transition(name="scroll-right")
    aside.page_sidebar(v-show="hideSidebar")
      ul.sidebar_tabset
        li(v-for="(tab, i) in tabset"
          :key="i"
        )
          button.btn(type="button"
            :class="{'active': i === tabSelected}"
            @click="selectTab(i)"
          ) {{tab}}

      .sidebar_tab(v-show="tabSelected === 0")
        //include ./sidebar/blocks/Project.pug
        sidebar-layers
        sidebar-comments
      .sidebar_tab(v-show="tabSelected === 1")
        include ./sidebar/blocks/Save.pug
      .sidebar_tab(v-show="tabSelected === 2")
        include ./sidebar/blocks/Import.pug
      .sidebar_tab(v-show="tabSelected === 3")
        include ./sidebar/blocks/Code.pug

</template>

<script>
  import SidebarLayers from '@/components/sidebar/sidebar-layers.vue'
  import SidebarComments from '@/components/sidebar/sidebar-comments.vue'

export default {
  name: 'TheSidebar',
  components: {
    SidebarLayers,
    SidebarComments
  },
  data() {
    return {
      tabset: ['Project', 'Save', 'Import', 'Code'],
      tabSelected: 0,
    }
  },
  computed: {
    hideSidebar() {
      return this.$store.state.globalView.hideSidebar
    }
  },
  methods: {
    selectTab(i) {
      this.tabSelected = i
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .page_sidebar {
    grid-area: sidebar;
    max-width: 300px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .sidebar_tabset {
    padding: 0;
    margin: 0;
    list-style: none;
    display: flex;
    flex: 0 0 auto;
    > li {
      flex: 1 1 50%;
      max-width: 50%;
      min-width: 75px;
    }
    .btn {
      border-radius: 0;
      height: 50px;
      width: 100%;
      background-color: $bg-toolbar;
      color: #8B8B9C;
      &.active {
        background-color: transparent;
        color: inherit;
      }
    }
  }
  .sidebar_tab {
    flex: 1 1 100%;
    display: flex;
    flex-direction: column;
    > * {
      width: 100%;
      flex: 1 1 auto;
    }
  }
  //Animations
  .scroll-right-enter-active, .scroll-right-leave-active {
    transition: max-width .5s;
  }
  .scroll-right-enter, .scroll-right-leave-to {
    max-width: 0;
  }
</style>
