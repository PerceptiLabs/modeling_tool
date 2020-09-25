<template lang="pug">
  .information-panel-container
    .information-panel-header
      div
        .information-panel-header-tab
          span(@click="onTabClick('ErrorInfoPanel')") Errors
        .information-panel-header-tab
          span(@click="onTabClick('ConsoleInfoPanel')") Console
      div 
        svg.close-window.clickable-icon(
          @click="closeWindow"
          viewBox="0 0 7 8"
          fill="none"
          xmlns="http://www.w3.org/2000/svg")
          path(
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M6.81187 7.03489C7.05234 6.80548 7.06381 6.4219 6.83748 6.17816L4.48982 3.64974L6.83748 1.12132C7.06381 0.877568 7.05234 0.493997 6.81187 0.264587C6.5714 0.0351768 6.193 0.0468001 5.96667 0.290548L3.23333 3.23435C3.01664 3.46772 3.01664 3.83175 3.23333 4.06512L5.96667 7.00892C6.193 7.25267 6.5714 7.2643 6.81187 7.03489Z"
            fill="white")
          path(
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M0.188129 0.264663C-0.0523387 0.494073 -0.0638057 0.877644 0.162517 1.12139L2.51018 3.64981L0.162516 6.17823C-0.0638062 6.42198 -0.0523392 6.80555 0.188128 7.03496C0.428596 7.26437 0.807004 7.25275 1.03333 7.009L3.76667 4.0652C3.98336 3.83183 3.98336 3.4678 3.76667 3.23443L1.03333 0.290624C0.807004 0.0468761 0.428596 0.0352527 0.188129 0.264663Z"
            fill="white")
    
    .perfect-scrollbar-padding-container

      component(:is="componentType")
</template>

<script>
import { mapState, mapActions } from 'vuex'
import ErrorInfoPanel   from '@/components/workspace/information-panel/information-panel-errors.vue'
import ConsoleInfoPanel from '@/components/workspace/information-panel/information-panel-console.vue'


export default {
  name: "InformationPanel",
  components: { ErrorInfoPanel, ConsoleInfoPanel },
  computed: {
    ...mapState({
      workspace:                  state => state.mod_workspace.workspaceContent,
      indexCurrentNetwork:        state => state.mod_workspace.currentNetwork,
    }),
    currentNetworkId() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId'];
    },
    getNotificationWindowSelectedTab() {
      return this.$store.getters['mod_workspace-notifications/getNotificationWindowSelectedTab'](this.workspace[this.indexCurrentNetwork].networkID);
    },
    componentType() {
      return this.getNotificationWindowSelectedTab || 'ErrorInfoPanel';
    },
  },
  methods: {
    onTabClick(tabName) {
      this.$store.dispatch("mod_workspace-notifications/setSelectedTabAction", {
        tabName,
        networkId: this.workspace[this.indexCurrentNetwork].networkID,
      });
    },
    closeWindow() {
      this.$store.dispatch('mod_workspace-notifications/setNotificationWindowState', {
        networkId: this.currentNetworkId,
        value: false,
        selectedTab: '',
      });
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
  
  $information-panel-header-height: 2rem;

  $information-panel-height: 30%;
  $information-panel-width: 70rem;

  $information-panel-font-size: 1.2rem;

  svg {
    height: 0.8rem;
    width: 0.8rem;
  }

  .clickable-icon {
    cursor: pointer;
  }

  .information-panel-container {
    position: absolute;

    height: $information-panel-height;
    width: $information-panel-width;
    z-index: 6;

    background: #1E1E1E;

    border: 1px solid #475D9C;
    box-sizing: border-box;

    right: 0;
    bottom: 0;

    overflow: hidden;
  }

  .information-panel-header {
    background: #3F4C70;

    display: flex;
    align-items: center;

    height: $information-panel-header-height;
    
    font-size: $information-panel-font-size;

    & > * {
      flex: 1;
      display: flex;
    }
    
    & > :first-child {
      justify-content: flex-start;

      margin-left: 1rem;
    }

    & > :last-child {
      justify-content: flex-end;
      
      & > * {
        margin-right: 1rem;
      }
    }

    .information-panel-header-tab {
      cursor: pointer;

      & + .information-panel-header-tab {
        margin-left: 2rem;
      }
    }
  }

  .perfect-scrollbar-padding-container {
    height: calc(100% - #{$information-panel-header-height});
    padding: 1rem;
  }
</style>
