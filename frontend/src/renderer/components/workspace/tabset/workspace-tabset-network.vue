<template lang="pug">
  ul.bookmark_tab-list
    li.bookmark_tab.workspace_tab(
    v-for="(tab, i) in workspace"
    :key="i"
    :class="{'workspace_tab--active': indexCurrentNetwork === i, 'workspace_tab--disable': indexCurrentNetwork !== i && isTutorialMode}"
    @click="setTabNetwork(i)"
    )
      button.btn.btn--icon.tab_close(type="button"
        :disabled="workspace.length <= 1"
        @click.stop="deleteTabNetwork(i)"
      )
        i.icon.icon-close
      text-editable.tab_name(
        :text-title="tab.networkName"
        @change-title="set_networkName"
        )
      button.btn.btn--tabs.tab_statistics#tutorial_statistic-tab(type="button"
        v-if="tab.networkMeta.openStatistics !== null"
        @click.stop="openStatistics(i)"
        :class="{'active': tab.networkMeta.openStatistics && indexCurrentNetwork === i}")
        span Statistics
        i.icon(:class="{'icon-circle-o': trainingWaiting(i), 'icon-circle-o green-color-icon': trainingInProcess(i), 'icon-ellipse green-color-icon': trainingFinished(i) }")
      button.btn.btn--tabs.tab_statistics.tab--testing(type="button"
        v-if="tab.networkMeta.openTest !== null"
        :class="{'active': tab.networkMeta.openTest && indexCurrentNetwork === i}"
        @click.stop="openTest(i)"
        )
        span Test
</template>

<script>
import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';

import TextEditable           from '@/components/base/text-editable.vue'

export default {
  components: {
    TextEditable
  },
  computed: {
    ...mapState({
      workspace:                  state => state.mod_workspace.workspaceContent,
      indexCurrentNetwork:        state => state.mod_workspace.currentNetwork,
    }),
    ...mapGetters({
      // currentSelectedEl:  'mod_workspace/GET_currentSelectedEl',
      testIsOpen:                 'mod_workspace/GET_testIsOpen',
      statisticsIsOpen:           'mod_workspace/GET_statisticsIsOpen',
    }),
    ...mapMutations({
      set_showTrainingSpinner:    'mod_workspace/SET_showStartTrainingSpinner',
      set_currentNetwork:         'mod_workspace/SET_currentNetwork',
      set_cursorPosition:         'mod_workspace/SET_CopyCursorPosition',
      set_cursorInsideWorkspace:  'mod_workspace/SET_cursorInsideWorkspace',
      set_hideSidebar:            'globalView/SET_hideSidebar',
    }),
    ...mapActions({
      setNetworkNameAction:       'mod_workspace/SET_networkName',
      set_elementUnselect:        'mod_workspace/SET_elementUnselect',
      set_chartRequests:          'mod_workspace/SET_chartsRequestsIfNeeded',
      set_openStatistics:         'mod_workspace/SET_openStatistics',
      set_openTest:               'mod_workspace/SET_openTest',
    }),    
  },
  methods: {
    trainingFinished(index) {
      let networkStatus = this.workspace[index].networkMeta.coreStatus.Status;
      return networkStatus === 'Finished' || networkStatus === 'Testing';
    },
    trainingInProcess(index) {
      let networkStatus = this.workspace[index].networkMeta.coreStatus.Status;
      return networkStatus === 'Training' || networkStatus === 'Validation';
    },
    trainingWaiting(index) {
      return this.workspace[index].networkMeta.coreStatus.Status === 'Waiting';
    },
    set_networkName(text) {
      this.setNetworkNameAction(text);
      this.pushSnapshotToHistory(null)
    },
    setTabNetwork(index) {
      this.set_showTrainingSpinner(false);
      if(this.statisticsIsOpen !== null) this.set_openStatistics(false);
      if(this.testIsOpen !== null) this.set_openTest(false);
      this.set_currentNetwork(index);
      this.set_elementUnselect();

      // request charts if the page has been refreshed, and 
      // the requested tab not being the first
      this.set_chartRequests(this.workspace[index].networkID);
    },
  }
}
</script>

<style lang="scss">
@import "../../../scss/base";

.workspace_tab {
  min-width: 16.7143em;
  display: flex;
  align-items: center;
  padding-right: 0;

  background-color: $bg-toolbar-2;
  border: 1px solid rgba(97, 133, 238, 0.2);
  border-top: 2px solid rgba(97, 133, 238, 0.2);
  border-radius: 2px 2px 0px 0px;

  &.workspace_tab--disable {
    pointer-events: none;
  }

  &.workspace_tab--active {
    border-top: 2px solid $color-6;
  }
}
.tab_close {
  margin-right: 1.25rem;
  font-size: .5em;
  color: $bg-scroll;
  &:disabled {
    opacity: 0;
  }
}
.tab_name {
  margin-right: 1rem;
  flex: 1;
}
.tab_statistics {
  height: 100%;
  padding: .25em 1.7em;
  border-radius: 1rem 1rem 0 0;
  font-size: 1rem;
  min-width: auto;
  .icon {
    font-size: 1.2em;
  }
  &.tab--testing {
    border-left: 1px solid;
    // margin-left: -1.25rem;
    padding-left: .8em;
    padding-right: .8em;
    &.active, &:hover {
      background: $color-10;
      color: $bg-toolbar;
    }
  }
}
</style>
