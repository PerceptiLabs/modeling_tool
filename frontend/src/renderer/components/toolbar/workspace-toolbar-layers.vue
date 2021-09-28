<template lang="pug">
  .layers-list-container
    .layer-list(
      v-for="(layer, idx) in layersbarList"
      :key="idx"
      @click.stop="toggleElList(idx)"
      @focusout="handleFocusOut"
      :data-tutorial-target="'tutorial-workspace-layer-menu'"
      tabindex="0"
    )

      .layer-list-header(
        :class="[{'active': showElementsInLayer(layer)}]"
        :data-tutorial-marker="'LayerMenuItem_' + layer.tooltip"
      )
        .layer-list-header-label.bold {{ layer.tooltip }}
        svg(width="9" height="6" viewBox="0 0 9 6" fill="none" xmlns="http://www.w3.org/2000/svg")
          path.bold(d="M3.91611 5.72652L0.193542 1.32977C-0.245778 0.812461 0.111266 2.94913e-07 0.778007 2.94913e-07H8.22315C8.37237 -0.000131902 8.51846 0.0441823 8.64393 0.127636C8.7694 0.211091 8.86893 0.330147 8.9306 0.470548C8.99227 0.610949 9.01347 0.766743 8.99166 0.919273C8.96985 1.0718 8.90595 1.2146 8.80762 1.33057L5.08505 5.72572C5.01219 5.81187 4.92235 5.88091 4.82154 5.92822C4.72073 5.97552 4.6113 6 4.50058 6C4.38986 6 4.28043 5.97552 4.17962 5.92822C4.07881 5.88091 3.98897 5.81187 3.91611 5.72572V5.72652Z")

      ul.layer_child-list(
        v-if="layer.networkElements"
        :class="layer.childListClass"
      )
        li.layer_child-list-item(
          v-for="(element, i) in layer.networkElements"
          :key="i"
          @mouseenter="mouseOver(element)"
          @mouseleave="mouseOut"
          @mousedown="onLayerClick($event, element)"
          :data-tutorial-target="element === 'DataData' ? 'tutorial-workspace-layer-data' : ''"
          ref="referenceMenuItem"
        )
          component(:is="element" :draggable="true" :showTitle="true" :ref="`layer-${element}`")

</template>

<script>
  import { trainingElements, deepLearnElements }  from '@/core/constants.js'
  import { mapActions, mapGetters }       from 'vuex';
  import {generateID, isEnvDataWizardEnabled} from "@/core/helpers.js";
  
  import DataData             from '@/components/network-elements/elements/data-data/view-data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/view-data-environment.vue'
  import DataRandom           from '@/components/network-elements/elements/data-random/view-data-random.vue'

  import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/view-deep-learning-fc.vue'
  import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/view-deep-learning-conv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/view-deep-learning-recurrent.vue'

  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/view-process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/view-process-grayscale.vue'
  import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/view-process-one-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape/view-process-reshape.vue'
  import ProcessRescale       from '@/components/network-elements/elements/process-rescale/view-process-rescale.vue'

  import TrainNormal          from '@/components/network-elements/elements/train-normal/view-train-normal.vue'
  import TrainRegression      from '@/components/network-elements/elements/train-regression/view-train-regression.vue';
  import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/view-train-reinforce.vue';
  import TrainGan             from '@/components/network-elements/elements/train-gan/view-train-gan.vue';
  import TrainDetector        from '@/components/network-elements/elements/train-detector/view-train-detector.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax/view-math-argmax.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge/view-math-merge.vue'

  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/view-classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/view-classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/view-classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/view-classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/view-classic-ml-vector-machine.vue'

  import IoInput              from '@/components/network-elements/elements/io-input/view-io-input.vue'
  import IoOutput             from '@/components/network-elements/elements/io-output/view-io-output.vue'

  import LayerCustom          from '@/components/network-elements/elements/layer-custom/view-layer-custom.vue'

  import PreTrainedVGG16        from '@/components/network-elements/elements/pretrained-vgg16/view-pretrained-vgg16.vue'
  import PreTrainedMobileNetV2  from '@/components/network-elements/elements/pretrained-mobilenetv2/view-pretrained-mobilenetv2.vue'
  import PreTrainedInceptionV3  from '@/components/network-elements/elements/pretrained-inceptionv3/view-pretrained-inceptionv3.vue'
  import PreTrainedResNet50   from '@/components/network-elements/elements/pretrained-resnet50/view-pretrained-resnet50.vue'
  import UNet                  from '@/components/network-elements/elements/unet/view-unet'; 

  import { calcLayerPosition } from '@/core/helpers.js';
  import { connectComponentsWithArrow } from '@/core/modelHelpers.js'

export default {
  name: 'WorkspaceToolbarLayers',
  components: {
    DataData, DataEnvironment, DataRandom,
    DeepLearningFC, DeepLearningConv, DeepLearningRecurrent,
    ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape, ProcessRescale,
    TrainNormal, TrainRegression, TrainReinforce, TrainDetector, TrainGan,
    MathArgmax, MathMerge,
    LayerCustom,
    PreTrainedVGG16, PreTrainedInceptionV3, PreTrainedResNet50, PreTrainedMobileNetV2, 
    IoInput, IoOutput,
    UNet
  },
  created(){
    document.addEventListener('keyup', this.handleShiftKeyState);
    document.addEventListener('keydown', this.handleShiftKeyState);
  },
  beforeDestroy() {
    document.removeEventListener('keyup', this.handleShiftKeyState);
    document.removeEventListener('keydown', this.handleShiftKeyState);
  },
  data() {
    return {
      hoveredElement: '',
      clickedElementName: null,
      clonedElement: null,
      previousAddedElementId: null,
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
          networkElements: isEnvDataWizardEnabled() ? ['DataData', 'DataEnvironment', 'DataRandom', 'IoInput'] : ['DataData', 'DataEnvironment', 'DataRandom'],
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
          networkElements: ['MathArgmax', 'MathMerge'],
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
        document.addEventListener('click', this.handleClickWithoutElementSelected)
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
      event.preventDefault();
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
      const xPosition = x - halfWidth;
      const yPosition = y - halfHeight;
      
      this.$store.dispatch('mod_addComponent/setDraggedComponnentPosition', {x:xPosition , y: yPosition});
      
      this.clonedElement.style.left = xPosition + 'px';
      this.clonedElement.style.top = yPosition + 'px';

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
        
        const networkScale = this.networkScale;

        let fakeEvent = {
          id: generateID(), // here should be generated id to know 
          target: {
            dataset: {
              layer: this.clonedElement.dataset.layer,
              type: this.clonedElement.dataset.type,
              component: this.clonedElement.dataset.component,
            },
            clientHeight: 0,
            clientWidth: 0
          },
          offsetX: calcLayerPosition(event.x - left, networkScale),
          offsetY: calcLayerPosition(event.y - top, networkScale),
        };

        const isShiftPressed = event.shiftKey;

        if(isShiftPressed) {
        
          if(this.previousAddedElementId !== null) { // is second element placed by holding shift key

            this.$store.dispatch('mod_workspace/ADD_element', { event: fakeEvent });
            
            connectComponentsWithArrow(this.previousAddedElementId, fakeEvent.id);
            

            this.previousAddedElementId = fakeEvent.id;
          } else {
            // place where firs component is added;
            this.$store.dispatch('mod_workspace/ADD_element', { event: fakeEvent });
            
              
            connectComponentsWithArrow(this.closestElId, fakeEvent.id)

            this.previousAddedElementId = fakeEvent.id;
            this.$store.dispatch('mod_addComponent/setFirstComponentDragged', false);
          }

        } else {
          this.$store.dispatch('mod_workspace/ADD_element', { event: fakeEvent });
          this.cleanupClickDropFunctionality();
        }
        
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
        iconElement.style.visibility = 'hidden';

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
      document.getElementById("app").appendChild(this.clonedElement);
      document.addEventListener('mousemove', this.startComponentPositionUpdates);
      this.clonedElement.addEventListener('mouseup', this.stopComponentPositionUpdates);
      document.addEventListener('contextmenu', this.handleCancelEvents);
      document.addEventListener('keyup', this.handleEscKeypress);
      this.$store.dispatch('mod_addComponent/setFirstComponentDragged', true);
    },
    cleanupClickDropFunctionality() {
      document.removeEventListener('mousemove', this.startComponentPositionUpdates);
      this.clonedElement.removeEventListener('mouseup', this.stopComponentPositionUpdates);
      document.removeEventListener('contextmenu', this.handleCancelEvents);
      document.removeEventListener('keyup', this.handleEscKeypress);

      if(this.clonedElement) {
        document.getElementById("app").removeChild(this.clonedElement);
      }
      this.previousAddedElementId = null;
      this.clickedElementName = null;
      this.clonedElement = null;
      this.handleFocusOut();
      this.$store.dispatch('mod_addComponent/setFirstComponentDragged', false);
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

    },
    handleClickWithoutElementSelected(event) {
      if(this.clickedElementName === null && this.clonedElement === null) {
        event.stopPropagation();
        this.handleFocusOut();
        document.removeEventListener('click', this.handleClickWithoutElementSelected);
      }
    },
    handleShiftKeyState(event) {
      const isShiftPressed = event.shiftKey;
      this.$store.dispatch('mod_addComponent/setShiftKey', isShiftPressed);
    },
    filterUnnecessaryLayers(){
      if(isEnvDataWizardEnabled()) {
        let newArr = [];
        this.layersbarList.map(obj => {
          if(obj.id !== 'tutorial_data' && obj.id !== 'tutorial_training') {
            newArr.push(obj);
          }
        })
        this.layersbarList = newArr;
      }
    }
  },
  computed: {
    ...mapGetters({
      getCurrentStepCode:   'mod_tutorials/getCurrentStepCode',
      getShowTutorialTips:  'mod_tutorials/getShowTutorialTips',
    }),
    networkScale() {
      return this.$store.getters['mod_workspace/GET_currentNetworkZoom'];
    },
    closestElId() {
      return this.$store.state['mod_addComponent'].closestElId;
    }
  },
  mounted() {
    this.filterUnnecessaryLayers();
    if (!isEnvDataWizardEnabled()) { return; }

    // const ioDropdown = {
    //   tooltip: 'IO',
    //   tooltip_interactive: {
    //     title: 'IO',
    //     text: 'IO components'
    //   },
    //   layerClass: 'net-element-custom',
    //   iconClass: 'icon-train-group',
    //   childListClass: '',
    //   showEl: false,
    //   networkElements: [ 'IoInput', 'IoOutput' ],
    //   id:'tutorial_io',
    //   color: 'rgba(204, 204, 204, 0.7)',
    //   borderColor: 'rgba(204, 204, 204, 0.2)',
    //   bottomColor: 'rgba(204, 204, 204, 0.4)'
    // }
    //
    // if (!this.layersbarList.some(listItem => listItem.tooltip === 'IO')) {
    //   this.layersbarList.push(ioDropdown);
    // }
  }
}
</script>

<style lang="scss" scoped>
  
  $indent: 0.5rem;
  $icon-size: 1.3rem;
  $toolbar-size: 2.6rem;
  $button-size: 2.5rem;

  .layers-list-container {
    display: flex;
    justify-content: space-evenly;
    height: $toolbar-size;
    margin: 0;
    padding: 0;
    list-style: none;
    transition: transform $animation-speed $animation-speed;
    transform: translateY(0);

    position: relative;
    z-index: 10;
  }

  .layer-list {
    margin-right: 30px;
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
  .active {

    box-shadow: 0px 4px 4px  rgba(theme-var($shadow-color), 0.35);
  }
    * + * {
      margin-left: 1rem;
    }

    .icon {
      margin-left: 6px;
    }

    .layer-list-header-label {
      font-size: 16px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  ul.layer_child-list {
    @include multi-transition (transform, opacity, visibility);
    position: relative;
    top: 2px;
    visibility: hidden;
    opacity: 0;

    box-sizing: border-box;
    border-radius: 0px 0px 2px 2px;
    
    width: inherit; 

    background: theme-var($neutral-8);
    box-shadow: 0px 4px 4px  rgba(100, 100, 100, 0.36);
    

    .layer_child-list-item {
      
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: center;
      
      // height: $toolbar-size;
      padding: 20px 10px; 
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
          font-size: 14px;
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
