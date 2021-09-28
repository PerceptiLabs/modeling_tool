<template lang="pug">
  .information-panel-container
    .information-panel-header
      div.information-panel-header-wrapper
        .btn.btn--small(
          @click="onTabClick('ErrorInfoPanel')"
          :class="getNotificationWindowSelectedTab === 'ErrorInfoPanel' ? 'btn--primary' : 'btn--secondary'"
          :style={marginRight: '20px', fontSize: '14px'}
        )
          span Problems
          span.count-label {{workspaceErrors}}
        .btn.btn--small(
          @click="onTabClick('ConsoleInfoPanel')"
          :class="getNotificationWindowSelectedTab === 'ConsoleInfoPanel' ? 'btn--primary' : 'btn--secondary'"
          :style={fontSize: '14px'}
        )
          span() Console
      div 
        error-cta.small(v-if="workspaceErrors")
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
import ErrorCta         from '@/components/error-cta.vue'

export default {
  name: "InformationPanel",
  components: { ErrorInfoPanel, ConsoleInfoPanel, ErrorCta },
  computed: {
    ...mapState({
      workspace:                  state => state.mod_workspace.workspaceContent,
      currentNetworkIndex:        state => state.mod_workspace.currentNetwork,
    }),
    currentNetworkId() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId'];
    },
    getNotificationWindowSelectedTab() {
      return this.$store.getters['mod_workspace-notifications/getNotificationWindowSelectedTab'](this.workspace[this.currentNetworkIndex].networkID);
    },
    componentType() {
      return this.getNotificationWindowSelectedTab || 'ErrorInfoPanel';
    },
    workspaceErrors() {
      return this.$store.getters['mod_workspace-notifications/getErrors'](this.workspace[this.currentNetworkIndex].networkID).length;
    },
  },
  methods: {
    onTabClick(tabName) {
      this.$store.dispatch("mod_workspace-notifications/setSelectedTabAction", {
        tabName,
        networkId: this.workspace[this.currentNetworkIndex].networkID,
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
  
  
  $information-panel-header-height: 30px;

  $information-panel-height: 40%;
  $information-panel-width: 70rem;

  $information-panel-font-size: 1.2rem;

  svg {
    height: 0.8rem;
    width: 0.8rem;
  }

  .icon-app-minimize {
    color: $color-6;
  }
  .clickable-icon {
    cursor: pointer;
  }

  .information-panel-container {
    position: absolute;

    height: $information-panel-height;
    width: $information-panel-width;
    z-index: 6;

    background: theme-var($neutral-8);

    border: $border-1;
    border-radius: 4px;
    box-sizing: border-box;

    right: 0;
    bottom: 0;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);

    overflow: hidden;
  }

  .information-panel-header {
    background: theme-var($neutral-7);
    border-bottom: $border-1;

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
  }

  .perfect-scrollbar-padding-container {
    height: calc(100% - #{$information-panel-header-height});
    padding: 1rem;
  }
  .count-label {
    display: inline-block;
    width: 25px;
    height: 25px;
    background-color: #D9E2FF;
    border: 1px solid $color-6;
    margin-left: 3px;
    border-radius: 50%;
    text-align: center;
    color: $color-6;
    font-size: 14px;
    line-height: 25px;
  }
  .information-panel-header-wrapper {
    padding: 10px;
    display: none;
  }
</style>