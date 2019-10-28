<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
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
              @click="closePopup()"
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
      isTutorialMode: 'mod_tutorials/getIstutorialMode',
    }),
  },
  methods: {
    ...mapMutations({
      tutorialNextActiveStep:   'mod_tutorials/SET_activeStepMainTutorial',
      closePopup:               'globalView/HIDE_allGlobalPopups',
      set_showTrainingSpinner:  'mod_workspace/SET_showStartTrainingSpinner'
    }),
    ...mapActions({
      pointActivate:      'mod_tutorials/pointActivate',
      API_startTraining:  'mod_api/API_startTraining',
      SET_openStatistics: 'mod_workspace/SET_openStatistics',
      SET_openTest:       'mod_workspace/SET_openTest',
    }),
    setTab(i) {
      this.tabSelected = i;
    },
    startTraining() {
      this.closePopup();
      this.API_startTraining();
      this.SET_openStatistics(true);
      this.SET_openTest(null);
      if(this.isTutorialMode) this.tutorialNextActiveStep('next');
      this.set_showTrainingSpinner(true);
    },
  }
}
</script>
<style lang="scss" scoped>
  .settings-layer_foot {
    justify-content: center;
  }
</style>
