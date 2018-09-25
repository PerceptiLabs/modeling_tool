<template lang="pug">
  transition(name="scroll-left")
    aside.page_layersbar(v-show="hideLayers" )
      ul.layersbar-list
        li.layer(
          v-for="(layer, i) in layersbarList"
          :key="i"
        )
          button.btn.btn--layersbar.layer_parent(type="button"
            @click="toggleElList(i)"
            :class="[layer.layerClass, {'active': layer.showEl}]"
          )
            i.icon(:class="layer.iconClass")
          ul.layer_child-list(
            v-if="layer.networkElements"
          )
            li(
              v-for="(element, i) in layer.networkElements"
              :key="i"
            )
              component(:is="element" :draggable='true')

              //div(v-else)
                button.btn.btn--layersbar(type="button" draggable="true"
                //:class="layer.layerClass"
                //:data-component="element.nameComponent"
                //:data-layer="element.nameLayer"
                )
                  i.icon(:class="element.iconClass")
        li.layer
          button.btn.btn--layersbar.net-element-add(type="button")
            i.icon.icon-add

</template>

<script>
  import IoInput          from '@/components/network-elements/view/view-io-input.vue'
  import IoOutput         from '@/components/network-elements/view/view-io-output.vue'
  import DataData         from '@/components/network-elements/view/view-data-data.vue'
  import DataEnvironment  from '@/components/network-elements/view/view-data-environment.vue'
  import LearnDeepConnect  from '@/components/network-elements/view/view-learn-deep-connect.vue'
  import LearnDeepConvolut  from '@/components/network-elements/view/view-learn-deep-convolut.vue'
  import LearnDeepDeconvolut  from '@/components/network-elements/view/view-learn-deep-deconvolut.vue'
  import LearnDeepRecurrent  from '@/components/network-elements/view/view-learn-deep-recurrent.vue'
  import ProcessCrop  from '@/components/network-elements/view/view-process-crop.vue'
  import ProcessEmbed  from '@/components/network-elements/view/view-process-embed.vue'
  import ProcessGrayscale  from '@/components/network-elements/view/view-process-grayscale.vue'
  import ProcessHot  from '@/components/network-elements/view/view-process-hot.vue'
  import ProcessReshape  from '@/components/network-elements/view/view-process-reshape.vue'
  import TrainNormal  from '@/components/network-elements/view/view-train-normal.vue'
  import TrainReinforce  from '@/components/network-elements/view/view-train-reinforce.vue'

  // let layersbarData = [
  //   {
  //     tooltip: 'I/O',
  //     layerClass: 'net-element-io',
  //     iconClass: 'icon-data-toggle',
  //     showEl: false,
  //     networkElements: [
  //       {
  //         comp: true,
  //         nameLayer: 'Input',
  //         nameComponent: 'IoInput',
  //         iconClass: 'icon-data-in'
  //       },
  //       {
  //         nameLayer: 'Output',
  //         nameComponent: 'io-output',
  //         iconClass: 'icon-data-out'
  //       }
  //     ]
  //   },
  //   {
  //     tooltip: 'Data',
  //     layerClass: 'net-element-data',
  //     iconClass: 'icon-data',
  //     showEl: false,
  //     networkElements: [
  //       {
  //         nameLayer: 'Data',
  //         nameComponent: 'data-data',
  //         iconClass: 'icon-data'
  //       },
  //       {
  //         nameLayer: 'Environment',
  //         nameComponent: 'data-environment',
  //         iconClass: 'icon-map'
  //       }
  //     ]
  //   },
  //   {
  //     tooltip: 'Processing',
  //     layerClass: 'net-element-process',
  //     iconClass: 'icon-settings',
  //     showEl: false,
  //     networkElements: [
  //       {
  //         nameLayer: 'Reshape',
  //         nameComponent: 'process-reshape',
  //         iconClass: 'icon-full-screen'
  //       },
  //       {
  //         nameLayer: 'Word Embedding',
  //         nameComponent: 'process-embed',
  //         iconClass: 'icon-put-in-button'
  //       },
  //       {
  //         nameLayer: 'Grayscale',
  //         nameComponent: 'process-grayscale',
  //         iconClass: 'icon-sieve'
  //       },
  //       {
  //         nameLayer: 'One Hot',
  //         nameComponent: 'process-hot',
  //         iconClass: 'icon-'
  //       },
  //       {
  //         nameLayer: 'Crop',
  //         nameComponent: 'process-crop',
  //         iconClass: 'icon-crop-symbol'
  //       }
  //     ]
  //   },
  //   {
  //     tooltip: 'Deep Learning',
  //     layerClass: 'net-element-learn-deep',
  //     iconClass: 'icon-network',
  //     showEl: false,
  //     networkElements: [
  //       {
  //         nameLayer: 'Fully Connected',
  //         nameComponent: 'learn-deep-connect',
  //         iconClass: 'icon-round'
  //       },
  //       {
  //         nameLayer: 'Convolution',
  //         nameComponent: 'learn-deep-convolut',
  //         iconClass: 'icon-round-out'
  //       },
  //       {
  //         nameLayer: 'Deconvolution',
  //         nameComponent: 'learn-deep-deconvolut',
  //         iconClass: 'icon-round-in'
  //       },
  //       {
  //         nameLayer: 'Recurrent',
  //         nameComponent: 'learn-deep-recurrent',
  //         iconClass: 'icon-round-left'
  //       }
  //     ]
  //   },
  //   {
  //     tooltip: 'Training',
  //     layerClass: 'net-element-train',
  //     iconClass: 'icon-',
  //     showEl: false,
  //     networkElements: [
  //       {
  //         nameLayer: 'Normal',
  //         nameComponent: 'train-normal',
  //         iconClass: 'icon-'
  //       },
  //       {
  //         nameLayer: 'Reinforcement Learning',
  //         nameComponent: 'train-reinforce',
  //         iconClass: 'icon-'
  //       }
  //     ]
  //   },
  //   {
  //     tooltip: 'Mathematics',
  //     layerClass: 'net-element-math',
  //     iconClass: 'icon-calc',
  //     showEl: false,
  //     networkElements: [
  //       {
  //         nameLayer: 'Split',
  //         nameComponent: 'math-split',
  //         iconClass: 'icon-road-split'
  //       },
  //       {
  //         nameLayer: 'Argmax',
  //         nameComponent: 'math-argmax',
  //         iconClass: 'icon-'
  //       },
  //       {
  //         nameLayer: 'Merge',
  //         nameComponent: 'math-merge',
  //         iconClass: 'icon-road-concat'
  //       },
  //       {
  //         nameLayer: 'Softmax',
  //         nameComponent: 'math-softmax',
  //         iconClass: 'icon-'
  //       }
  //     ]
  //   },
  //   {
  //     tooltip: 'Classic Machine Learning',
  //     layerClass: 'net-element-learn-class',
  //     iconClass: 'icon-mind',
  //     showEl: false,
  //     networkElements: [
  //       {
  //         nameLayer: 'K-Means Clustering',
  //         nameComponent: 'learn-class-k-means',
  //         iconClass: 'icon-round-sieve'
  //       },
  //       {
  //         nameLayer: 'DBSCAN',
  //         nameComponent: 'learn-class-dbscan',
  //         iconClass: 'icon-round-three'
  //       },
  //       {
  //         nameLayer: 'K Nearest Neighbor',
  //         nameComponent: 'learn-class-k-nearest',
  //         iconClass: 'icon-round-figur'
  //       },
  //       {
  //         nameLayer: 'Random Forest',
  //         nameComponent: 'learn-class-random-f',
  //         iconClass: 'icon-trees'
  //       },
  //       {
  //         nameLayer: 'Support Vector Machine',
  //         nameComponent: 'learn-class-vector',
  //         iconClass: 'icon-round-figur2'
  //       }
  //     ]
  //   },
  // ];

export default {
  name: 'TheLayersbar',
  components: {
    IoInput,
    IoOutput,
    DataData,
    DataEnvironment,
    LearnDeepConnect,
    LearnDeepConvolut,
    LearnDeepDeconvolut,
    LearnDeepRecurrent,
    ProcessCrop,
    ProcessEmbed,
    ProcessGrayscale,
    ProcessHot,
    ProcessReshape,
    TrainNormal,
    TrainReinforce,
  },
  data() {
    return {
      layersbarList: [
        {
          tooltip: 'I/O',
          layerClass: 'net-element-io',
          iconClass: 'icon-data-toggle',
          showEl: false,
          networkElements: ['IoInput', 'IoOutput']
        },
        {
          tooltip: 'Data',
          layerClass: 'net-element-data',
          iconClass: 'icon-data',
          showEl: false,
          networkElements: ['DataData', 'DataEnvironment']
            // {
            //   nameLayer: 'Data',
            //   nameComponent: 'data-data',
            //   iconClass: 'icon-data'
            // },
            // {
            //   nameLayer: 'Environment',
            //   nameComponent: 'data-environment',
            //   iconClass: 'icon-map'
            // }
          //]
        },
        {
          tooltip: 'Processing',
          layerClass: 'net-element-process',
          iconClass: 'icon-settings',
          showEl: false,
          networkElements: ['process-reshape', 'process-embed', 'process-grayscale', 'process-hot', 'process-crop']
            // {
            //   nameLayer: 'Reshape',
            //   nameComponent: 'process-reshape',
            //   iconClass: 'icon-full-screen'
            // },
            // {
            //   nameLayer: 'Word Embedding',
            //   nameComponent: 'process-embed',
            //   iconClass: 'icon-put-in-button'
            // },
            // {
            //   nameLayer: 'Grayscale',
            //   nameComponent: 'process-grayscale',
            //   iconClass: 'icon-sieve'
            // },
            // {
            //   nameLayer: 'One Hot',
            //   nameComponent: 'process-hot',
            //   iconClass: 'icon-'
            // },
            // {
            //   nameLayer: 'Crop',
            //   nameComponent: 'process-crop',
            //   iconClass: 'icon-crop-symbol'
            // }
          //]
        },
        {
          tooltip: 'Deep Learning',
          layerClass: 'net-element-learn-deep',
          iconClass: 'icon-network',
          showEl: false,
          networkElements: [ 'LearnDeepConnect', 'LearnDeepConvolut', 'LearnDeepDeconvolut', 'LearnDeepRecurrent',
            // {
            //   nameLayer: 'Fully Connected',
            //   nameComponent: 'learn-deep-connect',
            //   iconClass: 'icon-round'
            // },
            // {
            //   nameLayer: 'Convolution',
            //   nameComponent: 'learn-deep-convolut',
            //   iconClass: 'icon-round-out'
            // },
            // {
            //   nameLayer: 'Deconvolution',
            //   nameComponent: 'learn-deep-deconvolut',
            //   iconClass: 'icon-round-in'
            // },
            // {
            //   nameLayer: 'Recurrent',
            //   nameComponent: 'learn-deep-recurrent',
            //   iconClass: 'icon-round-left'
            // }
          ]
        },
        {
          tooltip: 'Training',
          layerClass: 'net-element-train',
          iconClass: 'icon-',
          showEl: false,
          networkElements: ['TrainNormal', 'TrainReinforce'
            // {
            //   nameLayer: 'Normal',
            //   nameComponent: 'train-normal',
            //   iconClass: 'icon-'
            // },
            // {
            //   nameLayer: 'Reinforcement Learning',
            //   nameComponent: 'train-reinforce',
            //   iconClass: 'icon-'
            // }
          ]
        },
        {
          tooltip: 'Mathematics',
          layerClass: 'net-element-math',
          iconClass: 'icon-calc',
          showEl: false,
          networkElements: [
            // {
            //   nameLayer: 'Split',
            //   nameComponent: 'math-split',
            //   iconClass: 'icon-road-split'
            // },
            // {
            //   nameLayer: 'Argmax',
            //   nameComponent: 'math-argmax',
            //   iconClass: 'icon-'
            // },
            // {
            //   nameLayer: 'Merge',
            //   nameComponent: 'math-merge',
            //   iconClass: 'icon-road-concat'
            // },
            // {
            //   nameLayer: 'Softmax',
            //   nameComponent: 'math-softmax',
            //   iconClass: 'icon-'
            // }
          ]
        },
        {
          tooltip: 'Classic Machine Learning',
          layerClass: 'net-element-learn-class',
          iconClass: 'icon-mind',
          showEl: false,
          networkElements: [
            // {
            //   nameLayer: 'K-Means Clustering',
            //   nameComponent: 'learn-class-k-means',
            //   iconClass: 'icon-round-sieve'
            // },
            // {
            //   nameLayer: 'DBSCAN',
            //   nameComponent: 'learn-class-dbscan',
            //   iconClass: 'icon-round-three'
            // },
            // {
            //   nameLayer: 'K Nearest Neighbor',
            //   nameComponent: 'learn-class-k-nearest',
            //   iconClass: 'icon-round-figur'
            // },
            // {
            //   nameLayer: 'Random Forest',
            //   nameComponent: 'learn-class-random-f',
            //   iconClass: 'icon-trees'
            // },
            // {
            //   nameLayer: 'Support Vector Machine',
            //   nameComponent: 'learn-class-vector',
            //   iconClass: 'icon-round-figur2'
            // }
          ]
        }
      ]
    }
  },
  computed: {
    hideLayers () {
      return this.$store.state.globalView.hideLayers
    }
  },
  methods: {
    toggleElList(index) {
      if (this.layersbarList[index].showEl) {
        this.layersbarList[index].showEl = false
      }
      else {
        this.closeElList();
        this.layersbarList[index].showEl = true;
      }
    },
    closeElList() {
      this.layersbarList.forEach((item)=> {
        item.showEl = false
      })
    }
  }
}
</script>

<style lang="scss">
  @import "../scss/base";
  $indent: 5px;
  .page_layersbar {
    grid-area: layersbar;
    max-width: $w-layersbar;
  }
  .layersbar-list {
    padding: 0;
    margin: 0;
    list-style: none;
    transform: translateY(0);
    transition: transform $animation-speed $animation-speed;
    padding-bottom: 30px;
  }
  .layer {
    position: relative;
    padding: $indent;
  }
  .layer_parent {
    position: relative;
    z-index: 1;
    &:after {
      content: "\e922";
      font-family: 'icomoon' !important;
      position: absolute;
      line-height: 1;
      right: 1px;
      bottom: 1px;
      font-size: 11px;
    }
  }
  .layer_child-list {
    @include multi-transition (transform, opacity, visibility);
    position: absolute;
    top: 0;
    left: -$indent;
    padding: $indent;
    margin: 0;
    list-style: none;
    opacity: 0;
    visibility: hidden;
    .active + & {
      transform: translateX(100%);
      opacity: 1;
      visibility: visible;
    }
    > li + li {
      padding-top: $indent;
    }
  }

  //Animations
  .scroll-left-enter {
    max-width: 0;
    .layersbar-list {
      transform: translateY(-120%);
    }
  }
  .scroll-left-enter-active {
    transition: max-width $animation-speed 0s;
  }
  .scroll-left-leave-active {
    transition: max-width $animation-speed $animation-speed;
    .layersbar-list {
      transition: transform $animation-speed;
    }
  }
  .scroll-left-leave-to {
    max-width: 0;
    .layersbar-list {
      transform: translateY(-120%);
    }
  }

</style>
