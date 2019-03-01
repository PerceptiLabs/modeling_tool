<template lang="pug">
  section.network_info-section
    .info-section_head(v-if="!testIsOpen")
      h3 Statistics
    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :elementData="elData.viewBox"
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
  import TrainNormalData  from '@/components/network-elements/elements/train-normal-data/viewBox-train-normal-data.vue'
  import TrainReinforce   from '@/components/network-elements/elements/train-reinforce/viewBox-train-reinforce.vue'


export default {
  name: "TheStatistics",
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

    }
  },
  methods: {

  },
  computed: {
      testIsOpen() {
        return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
      }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .open-test .the-statistics .info-section_main {
    border-left: 2px solid $bg-window;
  }
</style>
