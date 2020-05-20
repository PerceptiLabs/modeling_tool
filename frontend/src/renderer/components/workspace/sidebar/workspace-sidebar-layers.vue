<template lang="pug">
  aside.workspace_sidebar(
    :class="{'tutorial-active': activeStepStoryboard === 3}"
    v-if="!statisticsIsOpen && !testIsOpen")
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
    width: 20rem;
    z-index: 2;
  }

  .network.network--show-code {
    .workspace_sidebar {
      display: none;
    }
  }

</style>
