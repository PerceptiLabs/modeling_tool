<template lang="pug">
    .testing-head
    //- .testing-head
    //-   .testing-head_progress-bar-box
    //-     .progress-bar-box_progress(:style="{width: progress + '%'}")
    //-   .testing-head_controls  
    //-     button.controls-btn.i.icon.icon-player-prev
    //-     button.controls-btn.i.icon.icon-player-play
    //-     button.controls-btn.i.icon.icon-player-next
    //- .info-section_main(v-if="elData !== null")
    //-   component(
    //-     :is="elData.componentName"
    //-     :elementData="elData.viewBox"
    //-   )
</template>

<script>
  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/viewBox-classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/viewBox-classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/viewBox-classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/viewBox-classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/viewBox-classic-ml-vector-machine.vue'

  import TrainDynamic     from '@/components/network-elements/elements/train-dynamic/viewBox-train-dynamic.vue'
  import TrainGenetic     from '@/components/network-elements/elements/train-genetic/viewBox-train-genetic.vue'
  import TrainNormal      from '@/components/network-elements/elements/train-normal/viewBox-train-normal.vue'
  import TrainNormalData  from '@/components/network-elements/elements/train-normal-data/viewBox-train-normal-data.vue'
  import TrainReinforce   from '@/components/network-elements/elements/train-reinforce/viewBox-train-reinforce.vue'


export default {
  name: "TheTesting",
  components: {
    TrainNormal, TrainNormalData, TrainGenetic, TrainDynamic, TrainReinforce,
    ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,
  },
  props: {
    elData: {
      type: Object,
      default: function () {
        return {}
      }
    }
  },
  data() {
    return {
      progress: 30
    }
  },
  methods: {

  },
  computed: {

  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";

  .testing-head {
    border-top: 1px solid $color-10;
    background: $col-txt2;
  }
  .testing-head_progress-bar-box {
    width: 100%;
    height: 0.5rem;
    background: #151515;
  }
  .progress-bar-box_progress {
    height: 100%;
    background: $color-10;
  }
  .testing-head_controls {
    display: flex;
    justify-content: center;
    padding: 1rem 0;
  }
  .controls-btn {
    background: none;
    color: $color-10;
    font-size: 2.5rem;
  }

</style>
