<template lang="pug">
  section.network_info-section.tutorial-relative
    .info-section_head(v-show="!testIsOpen")
      h3 {{ sectionTitle }}
      view-box-btn-list(
        v-if="btnList"
        :tab-set="btnList"
        @set-current-btn="setCurrentBtn"
        )

    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :element-data="elData.viewBox"
        :current-tab="currentBtn"
        @btn-list="setBtnList"
        )
</template>

<script>
  /*statistics*/
  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/viewBox-classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/viewBox-classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/viewBox-classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/viewBox-classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/viewBox-classic-ml-vector-machine.vue'
  import TrainDynamic     from '@/components/network-elements/elements/train-dynamic/viewBox-train-dynamic.vue'
  import TrainGenetic     from '@/components/network-elements/elements/train-genetic/viewBox-train-genetic.vue'
  import TrainNormal      from '@/components/network-elements/elements/train-normal/viewBox-train-normal.vue'
  import TrainReinforce   from '@/components/network-elements/elements/train-reinforce/viewBox-train-reinforce.vue'
  import TrainLoss        from '@/components/network-elements/elements/train-loss/viewBox-train-loss.vue'
  import TrainOptimizer   from '@/components/network-elements/elements/train-optimizer/viewBox-train-optimizer.vue'
  import TrainGan         from '@/components/network-elements/elements/train-gan/viewBox-train-gan.vue'
  /*view box*/
  import DataData         from '@/components/network-elements/elements/data-data/viewBox-data-data.vue'
  import DataEnvironment  from '@/components/network-elements/elements/data-environment/viewBox-data-environment.vue'
  import DataCloud        from '@/components/network-elements/elements/data-cloud/viewBox-data-cloud.vue'
  import DeepLearningFC        from '@/components/network-elements/elements/deep-learning-fc/viewBox-deep-learning-fc.vue'
  import DeepLearningConv      from '@/components/network-elements/elements/deep-learning-conv/viewBox-deep-learning-conv.vue'
  import DeepLearningDeconv    from '@/components/network-elements/elements/deep-learning-deconv/viewBox-deep-learning-deconv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/viewBox-deep-learning-recurrent.vue'
  import ProcessCrop      from '@/components/network-elements/elements/process-crop/viewBox-process-crop.vue'
  import ProcessEmbed     from '@/components/network-elements/elements/process-embed/viewBox-process-embed.vue'
  import ProcessGrayscale from '@/components/network-elements/elements/process-grayscale/viewBox-process-grayscale.vue'
  import ProcessOneHot    from '@/components/network-elements/elements/process-one-hot/viewBox-process-one-hot.vue'
  import ProcessReshape   from '@/components/network-elements/elements/process-reshape/viewBox-process-reshape.vue'
  import MathArgmax   from '@/components/network-elements/elements/math-argmax/viewBox-math-argmax.vue'
  import MathMerge    from '@/components/network-elements/elements/math-merge/viewBox-math-merge.vue'
  import MathSoftmax  from '@/components/network-elements/elements/math-softmax/viewBox-math-softmax.vue'
  import MathSplit    from '@/components/network-elements/elements/math-split/viewBox-math-split.vue'

  import ViewBoxBtnList from '@/components/statistics/view-box-btn-list.vue'

  import { mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: "TheViewBox",
  components: {
    TrainNormal, TrainGenetic, TrainDynamic, TrainReinforce, TrainLoss, TrainOptimizer, TrainGan,
    ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,

    DataData, DataEnvironment, DataCloud,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape,
    MathArgmax, MathMerge, MathSoftmax, MathSplit,
    ViewBoxBtnList
  },
  props: {
    sectionTitle: {type: String},
    elData: {
      type: Object,
      default: function () {
        return null
      }
    }
  },
  data() {
    return {
      currentBtn: '',
      btnList: null,
      /*
      * btnList model
      *
      * btnList: {
      *   ButtonName: null,
      *   ButtonName: {
      *     btnId: 'string',
      *     btnClass: 'string',
      *     btnInteractiveInfo: {
      *       title: 'string',
      *       text: 'string'
      *     }
      *   },
      * },
      *
      * */
    }
  },
  computed: {
    ...mapGetters({
      activePoint:   'mod_tutorials/getActivePoint',
      testIsOpen:   'mod_workspace/GET_testIsOpen'
    }),
  },
  watch: {
    'elData.componentName': {
      handler() { this.resetBtnInfo() }
    }
  },
  methods: {
    ...mapActions({
      pointActivate:    'mod_tutorials/pointActivate'
    }),
    setBtnList(objList) {
      this.btnList = objList;
    },
    setCurrentBtn(name) {
      this.currentBtn = name;
    },
    resetBtnInfo() {
      this.currentBtn = '';
      this.btnList = null
    }
  }
}
</script>

<style lang="scss">
  @import "../../scss/base";
  .open-statistic .the-view-box .info-section_main {
    border-left: 2px solid $bg-window;
  }
  /*statistics*/
  .open-test .the-statistics .info-section_main {
    border-left: 2px solid $bg-window;
  }
  .info-section_head {
    border-top: 1px solid $color-5;
  }
</style>
