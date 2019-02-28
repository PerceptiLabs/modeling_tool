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
        button.btn.btn--link.icon.icon-player-prev(type="button" @click="postTestMove('previousStep')")
        button.btn.btn--link.icon.icon-player-play(type="button" @click="postTestStart()")
        button.btn.btn--link.icon.icon-player-next(type="button" @click="postTestMove('nextStep')")
    //-.info-section_main(v-if="elData !== null")
      component(
      //  :is="elData.componentName"
      //  :elementData="elData.viewBox"
      //)
</template>

<script>
export default {
  name: "TheTesting",
  data() {
    return {
      //progress: 30
    }
  },
  computed: {
    progress() {
      let prog = this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus.Progress;
      return Math.round(prog * 100);
    },
  },
  methods: {
    postTestStart() {
      this.$store.dispatch('mod_api/API_postTestPlay')
    },
    postTestMove(request) {
      this.$store.dispatch('mod_api/API_postTestMove', request);
      this.$store.commit('mod_events/set_charts_doRequest');
      this.$nextTick(()=>this.$store.commit('mod_events/set_charts_doRequest'));

    },
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
