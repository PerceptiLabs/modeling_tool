<template lang="pug">
  perfect-scrollbar.information-panel-content
    .error-section
      .section-header
        .section-header-caret-icon.clickable-icon(@click="toggleErrorSection")
          svg(v-if="showErrorSection" width="5" height="3" viewBox="0 0 5 3" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M0 0L2.5 2.5L5 0L0 0Z" fill="#E1E1E1")
          svg(v-else width="3" height="5" viewBox="0 0 3 5" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M0.25 5L2.75 2.5L0.25 1.09278e-07L0.25 5Z" fill="#E1E1E1")
        .section-header-icon
          svg(width="11" height="10" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(d="M4.60311 0.52108C4.9924 -0.173694 6.0076 -0.173693 6.39689 0.521081L10.8714 8.50661C11.2475 9.1779 10.7538 10 9.97446 10H1.02554C0.246238 10 -0.247494 9.1779 0.128646 8.50661L4.60311 0.52108Z" fill="#FE7373")
            path(d="M5 3.3335L6 3.33979L5.74675 6.44335H5.25325L5 3.3335ZM5.95455 6.9092V7.77794H5.04545V6.9092H5.95455Z" fill="#23252A")
        .section-header-label Errors ({{ numErrors }})
      .item-container(v-if="showErrorSection")
        .item(
          v-for="e in workspaceErrors"
          :key="e.id"
          :class="{selected: e.id === selectedId}"
          @click="onClickNotification(e.id)"
        ) 
          .item-header
            .item-header-icon.clickable-icon(@click="toggleItem(e.id)")
              svg(v-if="expandedItems.includes(e.id)" width="5" height="3" viewBox="0 0 5 3" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(fill-rule="evenodd" clip-rule="evenodd" d="M0 0L2.5 2.5L5 0L0 0Z" fill="#E1E1E1")
              svg(v-else width="3" height="5" viewBox="0 0 3 5" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(fill-rule="evenodd" clip-rule="evenodd" d="M0.25 5L2.75 2.5L0.25 1.09278e-07L0.25 5Z" fill="#E1E1E1")
            .item-header-label Type of message
          .item-message(v-if="expandedItems.includes(e.id)")
            .item-message-header Problem
            pre.item-message-content(
              @dblclick="onDblClickMessage(e.layerId)"
            ) {{ e.Message }}

    .warning-section
      .section-header
        .section-header-caret-icon.clickable-icon(@click="toggleWarningSection")
          svg(v-if="showWarningSection" width="5" height="3" viewBox="0 0 5 3" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M0 0L2.5 2.5L5 0L0 0Z" fill="#E1E1E1")
          svg(v-else width="3" height="5" viewBox="0 0 3 5" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M0.25 5L2.75 2.5L0.25 1.09278e-07L0.25 5Z" fill="#E1E1E1")
        .section-header-icon
          svg(width="11" height="10" viewBox="0 0 11 10" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(d="M4.60311 0.52108C4.9924 -0.173694 6.0076 -0.173693 6.39689 0.521081L10.8714 8.50661C11.2475 9.1779 10.7538 10 9.97446 10H1.02554C0.246238 10 -0.247494 9.1779 0.128646 8.50661L4.60311 0.52108Z" fill="#FECF73")
            path(d="M5 3.3335L6 3.33979L5.74675 6.44335H5.25325L5 3.3335ZM5.95455 6.9092V7.77794H5.04545V6.9092H5.95455Z" fill="#23252A")
        .section-header-label General ({{ numWarnings }})
      .item-container(v-if="showWarningSection")
        .item(
          v-for="w in workspaceWarnings"
          :key="w.id"
          :class="{selected: w.id === selectedId}"
          @click="onClickNotification(w.id)"
        ) 
          .item-header
            .item-header-icon.clickable-icon(@click="toggleItem(w.id)")
              svg(v-if="expandedItems.includes(w.id)" width="5" height="3" viewBox="0 0 5 3" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(fill-rule="evenodd" clip-rule="evenodd" d="M0 0L2.5 2.5L5 0L0 0Z" fill="#E1E1E1")
              svg(v-else width="3" height="5" viewBox="0 0 3 5" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(fill-rule="evenodd" clip-rule="evenodd" d="M0.25 5L2.75 2.5L0.25 1.09278e-07L0.25 5Z" fill="#E1E1E1")
            .item-header-label Type of message
          .item-message(v-if="expandedItems.includes(w.id)")
            .item-message-header Problem
            pre.item-message-content(
              @dblclick="onDblClickMessage(w.layerId)"
            ) {{ w.Message }}
</template>

<script>
import Spinner   from '@/components/different/start-training-spinner.vue'

export default {
  name: "ErrorInfoPanel",
  components: { Spinner },
  data() {
    return {
      // selectedId: '',
      showErrorSection: true,
      showWarningSection: true,
      expandedItems: []
    }
  },
  computed: {
    currentNetworkId() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId'];
    },
    numErrors() {
      return this.workspaceErrors.length || 0;
    },
    numWarnings() {
      return this.workspaceWarnings.length || 0;
    },
    workspaceErrors() {
      return this.$store.getters['mod_workspace-notifications/getErrors'](this.currentNetworkId);
    },
    workspaceWarnings() {
      return this.$store.getters['mod_workspace-notifications/getWarnings'](this.currentNetworkId);
    },
    selectedId() {
      return this.$store.getters['mod_workspace-notifications/getSelectedId'](this.currentNetworkId);
    }
  },
  methods: {
    onDblClickMessage(layerId) {
      if (!layerId) { return; }
      const element = this.$store.getters['mod_workspace/GET_networkElementById'](layerId);

      this.$store.dispatch('mod_workspace-code-editor/openEditor', {
        networkId: this.currentNetworkId,
        element: element,
      });
    },
    onClickNotification(selectedId) {
      this.$store.commit('mod_workspace-notifications/setSelectedId', {
        networkId: this.currentNetworkId,
        selectedId
      });
    },
    toggleErrorSection() {
      this.showErrorSection = !this.showErrorSection;
    },
    toggleWarningSection() {
      this.showWarningSection = !this.showWarningSection;
    },
    toggleItem(itemId) {
      const idx = this.expandedItems.indexOf(itemId);

      if (idx >= 0) { this.expandedItems.splice(idx, 1); }
      else { this.expandedItems.push(itemId); }
    },
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
  }

  .perfect-scrollbar-padding-container {
    height: calc(100% - #{$information-panel-header-height});
    padding: 1rem;
  }

  .information-panel-content {
    padding: 1rem;
    height: 100%;
    overflow-y: auto;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: $information-panel-font-size;
    line-height: 1.2rem;
    
    .section-header {
      display: flex;
      align-items: center;
      padding: 0.5rem 0;

      .section-header-caret-icon {
        margin-right: 1rem;
      }

      .section-header-icon {
        margin-right: 1rem;
      }
    }

    .item {
      

      .item-header {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        padding-left: 2rem;

        .item-header-icon {
          margin-right: 1rem;
        }
      }

      .item-message {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        min-height: 3rem;
        padding: 1rem 2rem 1rem 4rem;

        .item-message-header {
          font-weight: bolder;
        }

        pre.item-message-content {
          user-select: text;
          white-space: break-spaces;
          overflow: hidden;
          text-overflow: ellipsis;
      
          font-family: Nunito Sans;
          font-style: normal;
          font-weight: normal;
          font-size: $information-panel-font-size;
          line-height: normal;
        }
      }

      &.selected {
        .item-header {
          background: rgba(97, 133, 238, 0.75);
        }

        .item-message {
          background: rgba(97, 133, 238, 0.25);
        }
      }
    }
  }
</style>
