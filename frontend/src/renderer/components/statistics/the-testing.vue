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
        //- button#tutorial_play-test-button.tutorial-relative.btn.btn--link.icon.icon-player-play(type="button"
        //-   :class="doGlobalEvent ? 'icon-player-pause' : 'icon-player-play'"
        //-   @click="postTestStart()"
        //-   )
        //- button.btn.btn--link.icon.icon-player-next(
        //-   type="button" 
        //-   @click="postTestMove('nextStep')"
        //-   :data-tutorial-target="'tutorial-test-controls'")
        button.btn-menu-bar.mr-5(
          @click="postTestMove('nextStep')"
        ) Next Sample
          svg.next-sample-svg(width="10" height="8" viewBox="0 0 10 8" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M0.5 4.00071C0.5 3.85153 0.559263 3.70845 0.664753 3.60296C0.770242 3.49747 0.913316 3.43821 1.0625 3.43821H7.57963L5.16425 1.02396C5.05863 0.918338 4.99929 0.775083 4.99929 0.625711C4.99929 0.476338 5.05863 0.333083 5.16425 0.227461C5.26987 0.121838 5.41313 0.0625 5.5625 0.0625C5.71187 0.0625 5.85513 0.121838 5.96075 0.227461L9.33575 3.60246C9.38813 3.65471 9.42969 3.71678 9.45805 3.78512C9.48641 3.85346 9.50101 3.92672 9.50101 4.00071C9.50101 4.0747 9.48641 4.14796 9.45805 4.2163C9.42969 4.28464 9.38813 4.34671 9.33575 4.39896L5.96075 7.77396C5.85513 7.87958 5.71187 7.93892 5.5625 7.93892C5.41313 7.93892 5.26987 7.87958 5.16425 7.77396C5.05863 7.66834 4.99929 7.52508 4.99929 7.37571C4.99929 7.22634 5.05863 7.08308 5.16425 6.97746L7.57963 4.56321H1.0625C0.913316 4.56321 0.770242 4.50395 0.664753 4.39846C0.559263 4.29297 0.5 4.1499 0.5 4.00071Z" fill="#B6C7FB")

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
          this.$store.dispatch('mod_workspace/EVENT_onceDoRequest')
        })
      })
  },
  computed: {
    doGlobalEvent() {
      return this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent'];
    },
    progressStore() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus.Progress;
    },
    progress() {
      const progress = this.progressStore;
      const waitEvent = this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent'];
      if(waitEvent && this.progressStore === 1) {
        this.$store.dispatch('mod_workspace/EVENT_startDoRequest', false)
      }
      return (progress * 100).toFixed(1);
    },
  },
  methods: {
    postTestStart() {
      this.$store.dispatch('mod_api/API_postTestPlay');
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
  .next-sample-svg {
    margin-left: 5px;
  }
</style>
