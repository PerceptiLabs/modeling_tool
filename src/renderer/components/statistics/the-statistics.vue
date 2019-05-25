<template lang="pug">
  section#tutorial_statistics.network_info-section
    .info-section_head(v-if="!testIsOpen")
      h3 Statistics
    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :element-data="elData.viewBox"
      )
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
  import TrainReinforce   from '@/components/network-elements/elements/train-reinforce/viewBox-train-reinforce.vue'
  import { mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: "TheStatistics",
  components: {
    TrainNormal, TrainGenetic, TrainDynamic, TrainReinforce,
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
  mounted() {
    this.pointActivate({way: null, validation: this.activePoint.actions[0].id})
  },
  methods: {
    ...mapActions({
      pointActivate:    'mod_tutorials/pointActivate'
    })
  },
  computed: {
    ...mapGetters({
      activePoint:   'mod_tutorials/getActivePoint',
      testIsOpen:   'mod_workspace/GET_testIsOpen'
    }),
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .open-test .the-statistics .info-section_main {
    border-left: 2px solid $bg-window;
  }
  .info-section_head {
    border-top: 1px solid $color-5;
  }
</style>
