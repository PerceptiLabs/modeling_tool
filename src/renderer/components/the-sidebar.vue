<template lang="pug">
  aside.page_sidebar(:class="{'page_sidebar--hide': !hideSidebar, 'tutorial-active': activeStep === 3}")
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
    testIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
    },
    isTraining() {
      return this.$store.getters['mod_workspace/GET_networkIsTraining']
    },
    showTraining() {
      // let editLayer = this.$store.getters['mod_workspace/GET_networkCanEditLayers'];
      // return editLayer ? false : true;
      if(this.isTraining && this.statisticsIsOpen) {
        return true
      }
      else return false
    },
    activeStep() {
      return this.$store.state.mod_tutorials.activeStep
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
    transition: max-width .3s;
    &.page_sidebar--hide {
      max-width: 0;
    }
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
    width: $w-sidebar;
    > * {
      width: 100%;
    }
  }

  .testing-results {
    padding: 1rem;
    h3 {
      margin-bottom: 2rem;
    }
    .testing-results-title {
      margin: 2rem 0;
    }
    p {
      font-size: 1.2rem;
    }
  }

</style>
