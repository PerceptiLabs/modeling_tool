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
            :disabled="tabSelected != i"
          ) {{tab}}

      .sidebar_tab(v-show="tabSelected === 0")
        //include ./sidebar/blocks/Project.pug
        sidebar-layers
        sidebar-training(v-if="showTraining")
        //sidebar-comments(v-else)
        sidebar-share
      .sidebar_tab(v-show="tabSelected === 1")
        include ./sidebar/blocks/Save.pug
      .sidebar_tab(v-show="tabSelected === 2")
        include ./sidebar/blocks/Import.pug
      .sidebar_tab(v-show="tabSelected === 3")
        include ./sidebar/blocks/Code.pug

</template>

<script>
  import SidebarLayers    from '@/components/sidebar/sidebar-layers.vue'
  import SidebarComments  from '@/components/sidebar/sidebar-comments.vue'
  import SidebarShare     from '@/components/sidebar/sidebar-share.vue'
  import SidebarTraining  from "@/components/sidebar/sidebar-training";

export default {
  name: 'TheSidebar',
  components: {
    SidebarTraining,
    SidebarLayers,
    SidebarComments,
    SidebarShare
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
    },
    statusNetworkCore() {
      return this.$store.getters['mod_workspace/GET_networkCoreStatus']
    },
    showTraining() {
      if(this.statusNetworkCore === 'Training' || this.statusNetworkCore === 'Validation' || this.statusNetworkCore === 'Paused') {
        return true
      }
      else return false
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
    max-width: $w-sidebar;
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
      height: $h-toolbar;
      width: 100%;
      background-color: $bg-toolbar;
      color: $disable-txt;
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
    width: $w-sidebar;;
    > * {
      width: 100%;
      //flex: 1 1 auto;
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
