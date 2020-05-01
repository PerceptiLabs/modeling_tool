<template lang="pug">
  aside.workspace_sidebar(:class="{'page_sidebar--hide': !hideSidebar, 'tutorial-active': activeStepStoryboard === 3}")
    sidebar-layers

</template>

<script>
  import SidebarLayers    from '@/components/sidebar/sidebar-layers.vue'
  import { mapGetters } from 'vuex';

export default {
  name: 'TheSidebar',
  components: {
    SidebarLayers
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
  @import "../../../scss/base";
  .workspace_sidebar {
    display: flex;
    flex-direction: column;
    max-width: $w-sidebar;
    grid-area: sidebar;
    transition: max-width .3s;
    &.page_sidebar--hide {
      max-width: 0;
    }
  }

</style>
