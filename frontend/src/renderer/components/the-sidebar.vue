<template lang="pug">
  aside.page_sidebar(:class="{'page_sidebar--hide': !hideSidebar, 'tutorial-active': activeStepStoryboard === 3}")
    ul.sidebar_tabset
      li(v-for="(tab, i) in tabset"
        :key="i"
      )
        button.btn(type="button"
          :class="{'active': i === tabSelected}"
          @click="selectTab(i)"
          v-tooltip-interactive:bottom="tab.tooltipInfo"
        ) {{tab.name}}

    .sidebar_tab(v-if="tabSelected === 0")
      sidebar-layers(:class="showTraining ? 'training' : ''")
      sidebar-training(v-if="ifTraining" v-show="showTraining")
    .sidebar_tab(v-if="tabSelected === 1")
      user-profile
    .sidebar_tab(v-if="tabSelected === 2")
      import-data
    .sidebar_tab(v-if="tabSelected === 3")
      export-data

    sidebar-share

</template>

<script>
  import SidebarLayers    from '@/components/sidebar/sidebar-layers.vue'
  import SidebarComments  from '@/components/sidebar/sidebar-comments.vue'
  import SidebarShare     from '@/components/sidebar/sidebar-share.vue'
  import SidebarTraining  from "@/components/sidebar/sidebar-training";
  import ExportData       from "@/components/different/export-data.vue";
  import ImportData       from "@/components/different/import-data.vue";
  import UserProfile       from "@/components/different/user-profile.vue";
  import { mapGetters } from 'vuex';

export default {
  name: 'TheSidebar',
  components: {
    SidebarTraining, SidebarLayers, SidebarComments, SidebarShare,
    ExportData, ImportData, UserProfile
  },
  data() {
    return {
      tabset: [
        {
          name: 'Project',
          tooltipInfo: {
            title: 'Project',
            text: 'Get an overview of the project'
          }
        },
        {
          name: 'Profile',
          tooltipInfo: {
            title: 'Profile',
            text: 'View your profile'
          }
        },
        {
          name: 'Import',
          tooltipInfo: {
            title: 'Import',
            text: 'Import templates or pre-trained models'
          }
        },
        {
          name: 'Export',
          tooltipInfo: {
            title: 'Export',
            text: 'Export trained model or code.'
          }
        }
      ],
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
    ifTraining() {
      return this.isTraining ? true : false
    },
    showTraining() {
      return this.statisticsIsOpen ? true : false
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
      font-size: 1.2rem;
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
