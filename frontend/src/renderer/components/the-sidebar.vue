<template lang="pug">
aside.page_sidebar(:class="{ 'page_sidebar--hide': !hideSidebar }")
  ul.sidebar_tab_list
    li.sidebar_tab(
      v-for="tab in tabset",
      :class="{ active: tab === tabSelected }",
      @click="selectTab(tab)"
    )
      | {{ tab }}
  .sidebar_content
    sidebar-settings(v-if="tabSelected === 'Component'")
    sidebar-layers(
      v-if="tabSelected === 'Network'",
      :class="showTraining ? 'training' : ''"
    )
</template>

<script>
import SidebarLayers from "@/components/sidebar/sidebar-layers.vue";
import SidebarSettings from "@/components/sidebar/sidebar-settings.vue";
import { mapGetters, mapActions } from "vuex";

export default {
  name: "TheSidebar",
  components: {
    SidebarLayers,
    SidebarSettings,
  },
  data() {
    return {
      tabset: ["Component", "Network"],
      tabSelected: "Component",
    };
  },
  computed: {
    ...mapGetters({
      statisticsIsOpen: "mod_workspace/GET_statisticsIsOpen",
    }),
    hideSidebar() {
      return this.$store.state.globalView.hideSidebar;
    },
    showTraining() {
      return this.statisticsIsOpen ? true : false;
    },
  },
  methods: {
    ...mapActions({
      setSidebarStateAction: "globalView/hideSidebarAction",
    }),
    selectTab(i) {
      this.tabSelected = i;
    },
    toggleSidebar() {
      this.setSidebarStateAction(false);
    },
  },
};
</script>

<style lang="scss" scoped>
.sidebar-top-empty-space {
  height: 31px;
  min-height: 30px;
  width: 100%;
  background-color: $bg-toolbar-2;
}
.page_sidebar {
  position: relative;
  display: flex;
  flex-direction: column;
  max-width: $w-sidebar;
  min-width: $w-sidebar;
  max-height: calc(100vh - 138px);
  grid-area: sidebar;
  transition: min-width 0.3s, max-width 0.3s !important;
  background-color: $bg-toolbar-2;
  border: $border-1;

  &.page_sidebar--hide {
    max-width: 0;
    min-width: 0;
    transition: min-width 0.3s, max-width 0.3s !important;
    overflow: hidden;
  }

  &:not(.page_sidebar--hide) {
    animation: hide-scroll 0.3s;
  }

  @keyframes hide-scroll {
    from,
    to {
      overflow: hidden;
    }
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
.sidebar_content {
  display: flex;
  flex: 1 1 100%;
  flex-direction: column;
  width: $w-sidebar;
  overflow: hidden;
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

.sidebar_tab_list {
  position: relative;
  display: flex;
  font-size: 16px;
  top: -1px;
  left: -1px;
  right: -1px;
  width: calc(100% + 2px);
  cursor: pointer;
}

.sidebar_tab {
  flex: 1;
  text-align: center;
  padding: 17px;
  border: 1px solid transparent;

  &:not(.active) {
    background: var(--neutral-7);
    border: 1px solid var(--border-color);
  }
}
</style>
