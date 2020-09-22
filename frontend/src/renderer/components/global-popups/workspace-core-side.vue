<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="cancelTraining()")
    section.popup
      .popup-background
        ul.popup_tab-set
          button.popup_header(
          v-for="(tab, i) in tabs"
          :key="tab.i"
          v-coming-soon="tabSelected != i"
          @click="setTab(i)"
          :class="{'disable': tabSelected != i}"
          
          )
            h3(v-html="tab")
        .popup_tab-body
          .popup_body(
            :class="{'active': tabSelected == 0}"
          )
            .settings-layer_section.text-center
              p.big-text Start training
            .settings-layer_foot
              button.btn.btn--primary.btn--disabled(type="button"
                @click="cancelTraining()"
                ) Cancel
              button#tutorial_start-training.btn.btn--primary(type="button"
                v-tooltip-interactive:right="interactiveInfo.start"
                @click="startTraining()"
                ) Start
          .popup_body(
            :class="{'active': tabSelected == 1}"
          )
            .settings-layer_section.text-center
              p.big-text this functionality is in development

</template>

<script>
import { mapGetters, mapMutations, mapActions } from 'vuex';
export default {
  name: "SelectCoreSide",
  data() {
    return {
      tabSelected: 0,
      tabs: ['Computer', 'Cloud'],
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
      isTutorialMode: 'mod_tutorials/getIsTutorialMode',
      currentNetwork: 'mod_workspace/GET_currentNetwork',
    }),
  },
  methods: {
    ...mapMutations({
      closePopup:               'globalView/HIDE_allGlobalPopups',
      set_showTrainingSpinner:  'mod_workspace/SET_showStartTrainingSpinner',
      setChecklistItemComplete: 'mod_tutorials/setChecklistItemComplete',
    }),
    ...mapActions({
      setSidebarStateAction:  'globalView/hideSidebarAction',
      API_startTraining:      'mod_api/API_startTraining',
      SET_openStatistics:     'mod_workspace/SET_openStatistics',
      SET_openTest:           'mod_workspace/SET_openTest',
      SET_networkSnapshot:    'mod_workspace/SET_networkSnapshot',
      saveNetwork:            'mod_webstorage/saveNetwork',
      setViewType:            'mod_workspace/setViewType',
      setCurrentView:         'mod_tutorials/setCurrentView'
    }),
    setTab(i) {
      this.tabSelected = i;
    },
    cancelTraining() {
      this.setCurrentView('tutorial-workspace-view');
      this.closePopup();
    },
    startTraining() {
      this.closePopup();
      this.SET_networkSnapshot()
        .then(_ => this.saveNetwork(this.currentNetwork))
        .then(_ => {
          this.API_startTraining();
          this.SET_openStatistics(true);
          this.setViewType('statistic');
          this.SET_openTest(null);
          this.set_showTrainingSpinner(true);
          this.setSidebarStateAction(false);
          this.setChecklistItemComplete({ itemId: 'startTraining' });
          this.setCurrentView('tutorial-statistics-view');
        });
    },
  }
}
</script>
<style lang="scss" scoped>
  .settings-layer_foot {
    justify-content: center;
  }
</style>
