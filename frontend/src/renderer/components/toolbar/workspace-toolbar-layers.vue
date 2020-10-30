<template lang="pug">
  .layers-list-container
    .layer-list(
      v-for="(layer, idx) in layersbarList"
      :key="idx"
      :style="{ 'border-color': layer.borderColor, 'border-bottom-color': layer.bottomColor }"
      @click.stop="toggleElList(idx)"
      @focusout="handleFocusOut"
      tabindex="0"
    )

      .layer-list-header(
        :class="[{'active': showElementsInLayer(layer)}]"
        :data-tutorial-marker="'LayerMenuItem_' + layer.tooltip"
        :data-tutorial-target="layer.tooltip === 'Data' ? 'tutorial-workspace-layer-menu' : ''"
      )
        i.icon(:class="layer.iconClass")
        .layer-list-header-label {{ layer.tooltip }}

      ul.layer_child-list(
        v-if="layer.networkElements"
        :class="layer.childListClass"
      )
        li.layer_child-list-item(
          v-for="(element, i) in layer.networkElements"
          :key="i"
          @mouseenter="mouseOver(element)"
          @mouseleave="mouseOut"
          @click="onLayerClick($event, element)"
          @mousedown="onLayerClick($event, element)"
          :style="[calcLayerItemStyle(element, layer.color)]"
          :data-tutorial-target="element === 'DataData' ? 'tutorial-workspace-layer-data' : ''"
          ref="referenceMenuItem"
        )
          component(:is="element" :draggable="true" :showTitle="true" :ref="`layer-${element}`")

    //- .single-layer-category(
    //-   @click="onLayerClick($event, 'custom')"
    //- )
    //-   layer-custom(:draggable="true" :showTitle="true" ref="layer-custom")
    
</template>

<script>
  import {trainingElements, deepLearnElements}  from '@/core/constants.js'
  import { mapActions, mapGetters }       from 'vuex';

  import DataData             from '@/components/network-elements/elements/data-data/view-data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/view-data-environment.vue'
  import DataCloud            from '@/components/network-elements/elements/data-cloud/view-data-cloud.vue'
  import DataRandom            from '@/components/network-elements/elements/data-random/view-data-random.vue'

  import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/view-deep-learning-fc.vue'
  import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/view-deep-learning-conv.vue'
  import DeepLearningDeconv   from '@/components/network-elements/elements/deep-learning-deconv/view-deep-learning-deconv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/view-deep-learning-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop/view-process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/view-process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/view-process-grayscale.vue'
  import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/view-process-one-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape/view-process-reshape.vue'
  import ProcessRescale       from '@/components/network-elements/elements/process-rescale/view-process-rescale.vue'

  import TrainNormal          from '@/components/network-elements/elements/train-normal/view-train-normal.vue'
  import TrainRegression      from '@/components/network-elements/elements/train-regression/view-train-regression.vue'
  import TrainGenetic         from '@/components/network-elements/elements/train-genetic/view-train-genetic.vue'
  import TrainDynamic         from '@/components/network-elements/elements/train-dynamic/view-train-dynamic.vue'
  import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/view-train-reinforce.vue'
  import TrainLoss            from '@/components/network-elements/elements/train-loss/view-train-loss.vue'
  import TrainOptimizer       from '@/components/network-elements/elements/train-optimizer/view-train-optimizer.vue'
  import TrainGan             from '@/components/network-elements/elements/train-gan/view-train-gan.vue'
  import TrainDetector        from '@/components/network-elements/elements/train-detector/view-train-detector.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax/view-math-argmax.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge/view-math-merge.vue'
  import MathSwitch            from '@/components/network-elements/elements/math-switch/view-math-switch.vue'
  import MathSoftmax          from '@/components/network-elements/elements/math-softmax/view-math-softmax.vue'
  import MathSplit            from '@/components/network-elements/elements/math-split/view-math-split.vue'

  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/view-classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/view-classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/view-classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/view-classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/view-classic-ml-vector-machine.vue'

  import LayerCustom         from '@/components/network-elements/elements/layer-custom/view-layer-custom.vue'


export default {
  name: 'TheLayersbar',
  components: {
    DataData, DataEnvironment, DataRandom,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape, ProcessRescale,
    TrainNormal, TrainRegression, TrainGenetic, TrainDynamic, TrainReinforce, TrainDetector, TrainGan,
    MathArgmax, MathMerge, MathSoftmax, MathSwitch,
    LayerCustom
  },
  data() {
    return {
      hoveredElement: '',
      clickedElementName: null,
      clonedElement: null,
      layersbarList: [
        {
          tooltip: 'Data',
          tooltip_interactive: {
            title: 'Data',
            text: 'Choose between reading from </br> a source or an environment'
          },
          layerClass: 'net-element-data',
          iconClass: 'icon-data-group',
          childListClass: '',
          showEl: false,
          networkElements: ['DataData', 'DataEnvironment', 'DataRandom'],
          id:'tutorial_data',
          color: 'rgba(97, 133, 238, 0.7)',
          borderColor: 'rgba(97, 133, 238, 0.2)',
          bottomColor: 'rgba(97, 133, 238, 0.4)',
        },
        {
          tooltip: 'Processing',
          tooltip_interactive: {
            title: 'Processing',
            text: 'Process and transform the data.'
          },
          layerClass: 'net-element-process',
          iconClass: 'icon-processing-group',
          childListClass: '',
          showEl: false,
          networkElements: ['process-reshape', 'process-grayscale', 'ProcessOneHot', 'process-rescale'],
          id:'tutorial_processing',
          color: 'rgba(253, 205, 114, 0.7)',
          borderColor: 'rgba(253, 205, 114, 0.2)',
          bottomColor: 'rgba(253, 205, 114, 0.4)'
        },
        {
          tooltip: 'Deep Learning',
          tooltip_interactive: {
            title: 'Deep Learning',
            text: 'Deep learning components'
          },
          layerClass: 'net-element-learn-deep',
          iconClass: 'icon-deep-learning-group',
          childListClass: '',
          showEl: false,
          networkElements: deepLearnElements,
          id:'tutorial_deep-learning',
          color: 'rgba(241, 100, 100, 0.7)',
          borderColor: 'rgba(241, 100, 100, 0.2)',
          bottomColor: 'rgba(241, 100, 100, 0.4)'
        },
        {
          tooltip: 'Operations',
          tooltip_interactive: {
            title: 'Mathematics',
            text: 'Mathematical components'
          },
          layerClass: 'net-element-math',
          iconClass: 'icon-math-group',
          childListClass: '',
          showEl: false,
          networkElements: ['MathArgmax', 'MathMerge', 'MathSwitch', 'MathSoftmax'],
          id:'tutorial_mathematics',
          color: 'rgba(0, 123, 239, 0.7)',
          borderColor: 'rgba(0, 123, 239, 0.2)',
          bottomColor: 'rgba(0, 123, 239, 0.4)'
        },
        {
          tooltip: 'Training',
          tooltip_interactive: {
            title: 'Training',
            text: 'Training components'
          },
          layerClass: 'net-element-train',
          iconClass: 'icon-train-group',
          childListClass: '',
          showEl: false,
          networkElements: trainingElements,
          id:'tutorial_training',
          color: 'rgba(115, 254, 187, 0.7)',
          borderColor: 'rgba(115, 254, 187, 0.2)',
          bottomColor: 'rgba(115, 254, 187, 0.4)'
        },
        {
          tooltip: 'Custom',
          tooltip_interactive: {
            title: 'Custom',
            text: 'Custom components'
          },
          layerClass: 'net-element-custom',
          iconClass: 'icon-custom',
          childListClass: '',
          showEl: false,
          networkElements: ['LayerCustom'],
          id:'tutorial_custom',
          color: 'rgba(204, 204, 204, 0.7)',
          borderColor: 'rgba(204, 204, 204, 0.2)',
          bottomColor: 'rgba(204, 204, 204, 0.4)'
        },
      ],
    }
  },
  methods: {
    ...mapActions({
      setNextStep:              'mod_tutorials/setNextStep',
    }),
    toggleElList(idx) {
      
      if (this.layersbarList[idx].showEl) {
        this.layersbarList[idx].showEl = false;
      }
      else {
        this.layersbarList[idx].showEl = true;
      }

      this.setNextStep({currentStep:'tutorial-workspace-layer-menu'});
    },
    handleFocusOut() {
      this.layersbarList.forEach((item)=> {
        item.showEl = false
      });
    },
    mouseOver(elementName) {
      this.hoveredElement = elementName;
    },
    mouseOut() {
      this.hoveredElement = '';
    },
    calcLayerItemStyle(elementName, backgroundColor){
      const bgc = this.hoveredElement === elementName ? backgroundColor : '#23252A';

      return ({
        'background-color': bgc
      });
    },
    onLayerClick(event, elementName) {
      // This function handles the magic of cloning and setting up event listeners
      if (this.clickedElementName) {  return; }

      this.cloneElement(elementName);
      this.setClonedElementStyle();
      this.setupClickDropFunctionality();
    },
    startComponentPositionUpdates(event) {
      const x = event.clientX + (document.documentElement.scrollLeft ? document.documentElement.scrollLeft : document.body.scrollLeft);
	    const y = event.clientY + (document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop);
      
      const halfHeight = this.clonedElement.style.height.replace('px', '') / 2;
      const halfWidth = this.clonedElement.style.width.replace('px', '') / 2;
      
      this.clonedElement.style.left = (x - halfWidth) + 'px';
      this.clonedElement.style.top = (y - halfHeight) + 'px';
    },
    handleCancelEvents(event) {
      event.preventDefault();
      this.cleanupClickDropFunctionality();
    },
    stopComponentPositionUpdates(event) {
      const svg = document.querySelector('.svg-arrow');
      const {top, right, bottom, left} = svg.getBoundingClientRect();

      // This check is to make sure that the position of click is within the network field
      if (left <= event.x && 
          event.x <= right &&
          top <= event.y && 
          event.y <= bottom) {
        
        let fakeEvent = {
          target: {
            dataset: {
              layer: this.clonedElement.dataset.layer,
              type: this.clonedElement.dataset.type,
              component: this.clonedElement.dataset.component,
            },
            clientHeight: 0,
            clientWidth: 0
          },
          offsetX: event.x - left,
          offsetY: event.y - top
        };

        this.$store.dispatch('mod_workspace/ADD_element', { event: fakeEvent });

        this.cleanupClickDropFunctionality();
      }
    },
    cloneElement(elementName) {
      this.clickedElementName = `layer-${elementName}`;

      // The refs will be an array because of the v-for
      // Normal layers will evaluate to true; 'custom' will eval to false
      if (Array.isArray(this.$refs[this.clickedElementName])) {
        this.clonedElement = this.$refs[this.clickedElementName][0].$el.cloneNode(true);
      } else {
        this.clonedElement = this.$refs[this.clickedElementName].$el.cloneNode(true);
      }
    },
    setClonedElementStyle() {
        const referenceItem = this.$refs['referenceMenuItem'][0];

        this.clonedElement.classList.add('layer_child-list-item');
        this.clonedElement.style.height = referenceItem.offsetHeight + 'px';
        this.clonedElement.style.width = referenceItem.offsetWidth + 'px';
        this.clonedElement.style.background = 'transparent';
        this.clonedElement.style.zIndex = 10;
        this.clonedElement.style.position = 'absolute';
        this.clonedElement.style.cursor = "initial";
        this.clonedElement.style.border = "0";

        const iconElement = this.clonedElement.childNodes[0];
        const labelElement = this.clonedElement.childNodes[2];

        iconElement.style.fontSize = '1.3rem';
        labelElement.style.marginLeft = '1rem';
        labelElement.style.fontFamily = 'Nunito Sans';
        labelElement.style.fontStyle = 'normal';
        labelElement.style.fontWeight = 600;
        labelElement.style.fontSize = '1.1rem';
        labelElement.style.lineHeight = '1.6rem';
    },
    handleEscKeypress(event) {
      if (this.clickedElementName &&
          event.key === "Escape") {
          
        event.stopPropagation();
        this.cleanupClickDropFunctionality();
      }
    },
    setupClickDropFunctionality() {
      document.body.appendChild(this.clonedElement);
      document.addEventListener('mousemove', this.startComponentPositionUpdates);
      document.addEventListener('click', this.stopComponentPositionUpdates);
      document.addEventListener('contextmenu', this.handleCancelEvents);
      document.addEventListener('keyup', this.handleEscKeypress);
    },
    cleanupClickDropFunctionality() {
      document.removeEventListener('mousemove', this.startComponentPositionUpdates);
      document.removeEventListener('click', this.stopComponentPositionUpdates);
      document.removeEventListener('contextmenu', this.handleEscKeypress);
      document.removeEventListener('keyup', this.handleEscKeypress);

      document.body.removeChild(this.clonedElement);
      this.clickedElementName = null;
      this.clonedElement = null;
      this.handleFocusOut();
    },
    showElementsInLayer(layer) {
      if (layer.tooltip !== 'Data') {
        return layer.showEl;
      }
        
      if (this.getShowTutorialTips &&
          this.getCurrentStepCode === 'tutorial-workspace-layer-data') {
        return true;
      } else {
        return layer.showEl;
      }

    }
  },
  computed: {
    ...mapGetters({
      getCurrentStepCode:   'mod_tutorials/getCurrentStepCode',
      getShowTutorialTips:  'mod_tutorials/getShowTutorialTips',
    })
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  $indent: 0.5rem;
  $icon-size: 1.3rem;
  $toolbar-size: 2.6rem;
  $button-size: 2.5rem;

  .layers-list-container {
    display: flex;
    justify-content: space-evenly;
    height: $toolbar-size;
    width: 100%;
    margin: 0;
    padding: 0;
    list-style: none;
    transition: transform $animation-speed $animation-speed;
    transform: translateY(0);

    position: relative;
    z-index: 10;
  }

  .layer-list {
    height: 100%;
    width: 100%;

    box-sizing: border-box;
    background: #23252A;
    border-width: 1px;
    border-bottom-width: 3px;
    border-style: solid;
    border-color: rgba(77, 85, 106, 0.8);
    border-radius: 0px;
  }

  .layer {
    position: relative;

    + .layer {
      padding-left: $indent * 2;
    }
  }

  .layer-list-header {
    height: 100%;
    width: 100%;
    
    display: flex;  
    justify-content: center;
    align-items: center;

    box-sizing: border-box;

    cursor: pointer;

    * + * {
      margin-left: 1rem;
    }

    .icon {
      font-size: 1.3rem
    }

    .layer-list-header-label {
      font-family: Nunito Sans;
      font-style: normal;
      font-weight: 600;
      font-size: 1.2rem;
      line-height: 1.6rem;

      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  ul.layer_child-list {
    @include multi-transition (transform, opacity, visibility);
    position: relative;
    top: 2px;
    opacity: 0;
    visibility: hidden;

    box-sizing: border-box;
    border: 1px solid #3F4C70;
    border-radius: 0px 0px 2px 2px;
    
    width: inherit; 

    background: #23252A;

    .layer_child-list-item {
      
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;

      height: $toolbar-size;
      width: 100%; 

      position: relative;
      z-index: 10;

      pointer-events: auto;

      /deep/ .btn {
        height: 100%;
        width: 100%;

        border: 0;
        background: transparent;

        cursor: pointer;

        * + * {
//          margin-left: 1rem;
        }

        i {
          font-size: $icon-size;
          display: none;
        }

        .layerTitle {
          white-space: pre;
          font-size: 12px;
          font-family: Nunito Sans;
        }
      }

    }

    .active + & {
      visibility: visible;
      opacity: 1;
    } 
  }

  .single-layer-category {
    display: flex;
    justify-content: center;
    align-items: center;

    background: #23252A;
    border-width: 1px;
    border-bottom-width: 3px;
    border-style: solid;
    border-color: rgba(77, 85, 106, 0.2);
    border-bottom-color: rgba(77, 85, 106, 0.8);
    box-sizing: border-box;
    
    height: $toolbar-size;
    width: 100%; 

    /deep/ .btn.btn--layersbar.net-element-custom {
      height: 100%;
      width: 100%;

      font-family: Nunito Sans;
      font-style: normal;
      font-weight: 600;
      font-size: 1.2rem;
      line-height: 1.6rem;

      border: 0;

      background: transparent;

      cursor: pointer;

      * + * {
        margin-left: 1rem;
      }

      i {
        font-size: $icon-size;
      }
    }
  }
</style>
