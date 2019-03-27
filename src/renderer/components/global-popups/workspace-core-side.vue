<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      ul.popup_tab-set
        button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
        :disabled="tabSelected != i"
        )
          h3(v-html="tab")
      .popup_tab-body
        .popup_body(
          :class="{'active': tabSelected == 0}"
        )
          .settings-layer_section.text-center
            p.big-text Start training
          .settings-layer_foot
            button.btn.btn--dark-blue(type="button" @click="closePopup()") Cancel
            button.btn.btn--dark-blue(type="button" @click="startTraining()") Start
        .popup_body(
          :class="{'active': tabSelected == 1}"
        )
          .settings-layer_section.text-center
            p.big-text this functionality is in development

</template>

<script>
//import mixinSet       from '@/core/mixins/net-element-settings.js';
import { mapGetters, mapMutations, mapActions } from 'vuex';
export default {
  name: "SelectCoreSide",
  //mixins: [mixinSet],
  data() {
    return {
      tabSelected: 0,
      tabs: ['Computer', 'Cloud'],
      settings: {

      }
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:   'mod_tutorials/getIstutorialMode',
    }),
  },
  methods: {
    ...mapMutations({
      tutorialNextActiveStep:        'mod_tutorials/SET_activeStepMainTutorial'
    }),
    ...mapActions({
      pointActivate:    'mod_tutorials/pointActivate'
    }),
    setTab(i) {
      this.tabSelected = i;
    },
    startTraining() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
      this.$store.dispatch('mod_api/API_startTraining');
      this.$store.dispatch('mod_statistics/STAT_defaultSelect');
      this.$store.dispatch('mod_workspace/SET_openStatistics', true);
      if(this.isTutorialMode) {
        this.tutorialNextActiveStep('next')
      } 
    },
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
