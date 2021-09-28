<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="cancelTraining()")
    section.popup.popup-small
      .popup-background
        h1.popup-title.bold(class="text-center") Resume training?
        
        .popup_tab-body
          .popup_body(
            :class="{'active': tabSelected == 0}"
          )
            .settings-layer_section.text-center
              p.big-text Start training from latest epoch?
            .settings-layer_foot
              button.btn.btn--primary.btn--disabled(type="button"
                @click="startTraining(false)"
                ) No
              button#tutorial_start-training.btn.btn--primary(type="button"
                v-tooltip-interactive:right="interactiveInfo.start"
                @click="startTraining(true)"
                ) Yes
          .popup_body(
            :class="{'active': tabSelected == 1}"
          )
            .settings-layer_section.text-center
              p.big-text this functionality is in development

</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: "SelectCoreSide",
  data() {
    return {
      tabSelected: 0,
      tabs: ['Training'],
      settings: {},
      interactiveInfo: {
        start: {
          title: 'Start Training',
          text: ''
        }
      }
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:   'mod_tutorials/getIsTutorialMode',
      currentNetwork:   'mod_workspace/GET_currentNetwork',
      networkHasErrors: 'mod_workspace-notifications/getHasErrors'
    }),
    ...mapState({
      currentNetworkIndex:           state => state.mod_workspace.currentNetwork,
    })
  },
  methods: {
    ...mapMutations({
      GP_showCoreSideSettings:               'globalView/GP_showCoreSideSettings',
      set_showTrainingSpinner:  'mod_workspace/SET_showStartTrainingSpinner',
      updateCheckpointPaths:    'mod_workspace/updateCheckpointPaths',
      setCurrentStatsIndex:     'mod_workspace/set_currentStatsIndex'
    }),
    ...mapActions({
      setSidebarStateAction:    'globalView/hideSidebarAction',
      API_startTraining:        'mod_api/API_startTraining',
      SET_openStatistics:       'mod_workspace/SET_openStatistics',
      SET_openTest:             'mod_workspace/SET_openTest',
      SET_networkSnapshot:      'mod_workspace/SET_networkSnapshot',
      saveNetwork:              'mod_webstorage/saveNetwork',
      setViewType:              'mod_workspace/setViewType',
      setCurrentView:           'mod_tutorials/setCurrentView',
      setChecklistItemComplete: 'mod_tutorials/setChecklistItemComplete',
    }),    
    closePopup() {
      this.GP_showCoreSideSettings(false);
    },
    setTab(i) {
      this.tabSelected = i;
    },
    cancelTraining() {
      this.setCurrentView('tutorial-workspace-view');
      this.closePopup();
    },
    startTraining(withWeights = false) {
      this.closePopup();
      this.updateCheckpointPaths();

      this.$store.dispatch('mod_workspace/saveCurrentModelAction')
        .then(_ => {
          this.API_startTraining({ loadCheckpoint: withWeights });
          this.setCurrentStatsIndex(this.currentNetworkIndex);
          this.$store.commit('mod_workspace/update_network_meta', {key: 'coreStatus', networkID: this.currentNetwork.networkID, value: {Status: 'Created'}});
          this.SET_openStatistics(true);
          this.setViewType('statistic');
          this.SET_openTest(null);
          this.set_showTrainingSpinner(true);
          this.setSidebarStateAction(false);
          this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
          if(!this.networkHasErrors(this.currentNetwork.networkID)) {
            this.setChecklistItemComplete({ itemId: 'startTraining' });
          }
          this.setCurrentView('tutorial-statistics-view');
        });
    }
  }
}
</script>
<style lang="scss" scoped>
  .settings-layer_foot {
    justify-content: center;
  }
</style>
