<template lang="pug">
  .information-panel-container
    .information-panel-header
      div.information-panel-header-wrapper
        .information-panel-header-tab(
          :class="{'is-active': getNotificationWindowSelectedTab === 'ErrorInfoPanel'}"
        )
          span(@click="onTabClick('ErrorInfoPanel')") Errors
          span.count-label {{workspaceErrors}}
        .information-panel-header-tab(
          :class="{'is-active': getNotificationWindowSelectedTab === 'ConsoleInfoPanel'}"
        )
          span(@click="onTabClick('ConsoleInfoPanel')") Console
      div 
        i(
          @click="closeWindow"
          type="button"
          class="icon icon-app-minimize btn btn--icon clickable-icon")

    
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
    workspaceErrors() {
      return this.$store.getters['mod_workspace-notifications/getErrors'](this.workspace[this.indexCurrentNetwork].networkID).length;
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
    // background: #3F4C70;
    border-bottom: 1px solid #475D9C;

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
      position: relative;
      color: #C4C4C4;
      & + .information-panel-header-tab {
        margin-left: 2rem;
      }
      &.is-active {
        color: #fff;
        font-weight: bold;
        &:after {
          content: '';
          position: absolute;
          width: 100%;
          height: 1px;
          background-color: #fff;
          bottom: -3.5px;
          left: 0;
          font-size: 9px;
        }
      }
    }
  }

  .perfect-scrollbar-padding-container {
    height: calc(100% - #{$information-panel-header-height});
    padding: 1rem;
  }
  .count-label {
    display: inline-block;
    width: 14px;
    height: 14px;
    background-color: #363E51;
    margin-left: 3px;
    border-radius: 50%;
    text-align: center;
    font-size: 9px;
    line-height: 14px;
  }
  .information-panel-header-wrapper {
    padding: 10px;
  }
</style>