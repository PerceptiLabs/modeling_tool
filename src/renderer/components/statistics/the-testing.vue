<template lang="pug">
  section
    .testing-head
      .info-section_head
        .w-50
          h3 Input
        .w-50
          h3 Output
      .testing-head_progress-bar-box
        .progress-bar-box_progress(:style="{width: progress + '%'}")
      .testing-head_controls
        //-button.btn.btn--link.icon.icon-player-prev(type="button" @click="postTestMove('previousStep')")
        button#tutorial_play-test-button.tutorial-relative.btn.btn--link.icon.icon-player-play(type="button" @click="postTestStart()")
        button.btn.btn--link.icon.icon-player-next(type="button" @click="postTestMove('nextStep')")
    //-.info-section_main(v-if="elData !== null")
      component(
      //  :is="elData.componentName"
      //  :elementData="elData.viewBox"
      //)
</template>

<script>
import { mapActions } from 'vuex';
export default {
  name: "TheTesting",
  mounted() {
    this.getStatus();
    this.$store.dispatch('mod_api/API_postTestStart')
      .then(()=>{
        this.$nextTick(()=> {
          if(this.progressStore === 0) {
            this.postTestMove('nextStep')
          }
          else this.$store.dispatch('mod_workspace/EVENT_onceDoRequest')
        })
      })
  },
  computed: {
    progressStore() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus.Progress;
    },
    progress() {
      const progress = this.progressStore;
      const waitEvent = this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent'];
      if(waitEvent && this.progressStore === 1) this.postTestStart();
      return (progress * 100).toFixed(1);
    },
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    postTestStart() {
      this.$store.dispatch('mod_api/API_postTestPlay');
      this.tutorialPointActivate({way:'next', validation:'tutorial_play-test-button'})
    },
    postTestMove(request) {
      this.$store.dispatch('mod_api/API_postTestMove', request);
    },
    getStatus() {
      this.$store.dispatch('mod_api/API_getStatus');
    }
  },
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";

  .testing-head {
    border-top: 1px solid $color-10;
    //background: $bg-toolbar;
  }
  .testing-head_progress-bar-box {
    width: 100%;
    height: 0.5rem;
    background: #151515;
  }
  .progress-bar-box_progress {
    @include multi-transition(width);
    height: 100%;
    background: $color-10;
  }
  .testing-head_controls {
    display: flex;
    justify-content: center;
    padding: 1rem 0;
    background-color: $bg-workspace;
    .btn {
      color: $color-10;
      font-size: 2.5rem;
      margin: 0 .25em;
    }
  }

</style>
