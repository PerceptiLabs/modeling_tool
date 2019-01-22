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
    statisticsIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openStatistics
    },
    isTraining() {
      return this.$store.getters['mod_workspace/GET_networkIsTraining']
    },
    showTraining() {
      if(this.isTraining && this.statisticsIsOpen) {
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
    display: flex;
    overflow: hidden;
    flex-direction: column;
    max-width: $w-sidebar;

    grid-area: sidebar;
  }
  .sidebar_tabset {
    display: flex;
    flex: 0 0 auto;
    margin: 0;
    padding: 0;
    list-style: none;
    > li {
      flex: 1 1 50%;
      min-width: 75px;
      max-width: 50%;
    }
    .btn {
      color: $disable-txt;
      width: 100%;
      height: $h-toolbar;
      border-radius: 0;
      background-color: $bg-toolbar;
      &.active {
        color: inherit;
        background-color: transparent;
      }
    }
  }
  .sidebar_tab {
    display: flex;
    flex: 1 1 100%;
    flex-direction: column;
    width: $w-sidebar;;
    > * {
      width: 100%;
      //flex: 1 1 auto;
    }
  }
  //Animations
  .scroll-right-enter-active,
  .scroll-right-leave-active {
    transition: max-width .5s;
  }
  .scroll-right-enter,
  .scroll-right-leave-to {
    max-width: 0;
  }
</style>
