<template lang="pug">
  .notifications-window-container
    .notifications-window-header      
      div Errors
      div
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
      perfect-scrollbar.notifications-window-content
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
  name: "NotificationsWindow",
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
    closeWindow() {
      this.$store.dispatch('mod_workspace-notifications/setNotificationWindowState', {
        networkId: this.currentNetworkId,
        value: false
      });
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
  
  $notifications-window-header-height: 2rem;

  $notifications-window-height: 30%;
  $notifications-window-width: 70rem;

  $notifications-window-font-size: 1.2rem;

  svg {
    height: 0.8rem;
    width: 0.8rem;
  }

  .clickable-icon {
    cursor: pointer;
  }

  .notifications-window-container {
    position: absolute;

    height: $notifications-window-height;
    width: $notifications-window-width;
    z-index: 6;

    background: #1E1E1E;

    border: 1px solid #475D9C;
    box-sizing: border-box;

    right: 0;
    bottom: 0;

    overflow: hidden;
  }

  .notifications-window-header {
    background: #3F4C70;

    display: flex;
    align-items: center;

    height: $notifications-window-header-height;
    
    font-size: $notifications-window-font-size;

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
    height: calc(100% - #{$notifications-window-header-height});
    padding: 1rem;
  }

  .notifications-window-content {
    padding: 1rem;
    height: 100%;
    overflow-y: auto;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: $notifications-window-font-size;
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
          white-space: pre;
          overflow: hidden;
          text-overflow: ellipsis;
      
          font-family: Nunito Sans;
          font-style: normal;
          font-weight: normal;
          font-size: $notifications-window-font-size;
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
