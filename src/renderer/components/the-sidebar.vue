<template lang="pug">
  aside.page_sidebar(:class="{'page_sidebar--hide': !hideSidebar, 'tutorial-active': activeStepStoryboard === 3}")
    ul.sidebar_tabset
      li(v-for="(tab, i) in tabset"
        :key="i"
      )
        button.btn(type="button"
          :class="{'active': i === tabSelected}"
          @click="selectTab(i)"
        ) {{tab}}

    .sidebar_tab(v-if="tabSelected === 0")
      sidebar-layers
      sidebar-training(v-if="showTraining")
      sidebar-share
    .sidebar_tab(v-if="tabSelected === 1")
      include ./sidebar/blocks/Save.pug
    .sidebar_tab(v-if="tabSelected === 2")
      import-data
    .sidebar_tab(v-if="tabSelected === 3")
      export-data

</template>

<script>
  import SidebarLayers    from '@/components/sidebar/sidebar-layers.vue'
  import SidebarComments  from '@/components/sidebar/sidebar-comments.vue'
  import SidebarShare     from '@/components/sidebar/sidebar-share.vue'
  import SidebarTraining  from "@/components/sidebar/sidebar-training";
  import ExportData       from "@/components/different/export-data.vue";
  import ImportData       from "@/components/different/import-data.vue";
  import { mapGetters } from 'vuex';

export default {
  name: 'TheSidebar',
  components: {
    SidebarTraining,
    SidebarLayers,
    SidebarComments,
    SidebarShare,
    ExportData,
    ImportData
  },
  data() {
    return {
      tabset: ['Project', 'Profile', 'Import', 'Export'],
      tabSelected: 0,
    }
  },
  computed: {
    ...mapGetters({
      statisticsIsOpen: 'mod_workspace/GET_statisticsIsOpen',
      testIsOpen:       'mod_workspace/GET_testIsOpen',
      isTraining:       'mod_workspace/GET_networkIsTraining',
    }),
    hideSidebar() {
      return this.$store.state.globalView.hideSidebar
    },
    showTraining() {
      return (this.isTraining && this.statisticsIsOpen) ? true : false
    },
    activeStepStoryboard() {
      return this.$store.state.mod_tutorials.activeStepStoryboard
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
      min-width: 5rem;
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
