import DataData             from '@/components/network-elements/elements/data-data/data-data.vue'
import DataEnvironment      from '@/components/network-elements/elements/data-environment/data-environment.vue'
import DataCloud            from '@/components/network-elements/elements/data-cloud/data-cloud.vue'
import DataRandom            from '@/components/network-elements/elements/data-random/data-random.vue'

import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/deep-learning-fc.vue'
import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/deep-learning-conv.vue'
import DeepLearningDeconv   from '@/components/network-elements/elements/deep-learning-deconv/deep-learning-deconv.vue'
import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/deep-learning-recurrent.vue'

import ProcessCrop          from '@/components/network-elements/elements/process-crop/process-crop.vue'
import ProcessEmbed         from '@/components/network-elements/elements/process-embed/process-embed.vue'
import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/process-grayscale.vue'
import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/process-one-hot.vue'
import ProcessReshape       from '@/components/network-elements/elements/process-reshape/process-reshape.vue'
import ProcessRescale       from '@/components/network-elements/elements/process-rescale/process-rescale.vue'

import TrainNormal          from '@/components/network-elements/elements/train-normal/train-normal.vue'
import TrainRegression          from '@/components/network-elements/elements/train-regression/train-regression.vue'
import TrainGenetic         from '@/components/network-elements/elements/train-genetic/train-genetic.vue'
import TrainDynamic         from '@/components/network-elements/elements/train-dynamic/train-dynamic.vue'
import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/train-reinforce.vue'
import TrainLoss            from '@/components/network-elements/elements/train-loss/train-loss.vue'
import TrainOptimizer       from '@/components/network-elements/elements/train-optimizer/train-optimizer.vue'
import TrainDetector       from '@/components/network-elements/elements/train-detector/train-detector.vue'
import TrainGan       from '@/components/network-elements/elements/train-gan/train-gan.vue'

import MathArgmax           from '@/components/network-elements/elements/math-argmax/math-argmax.vue'
import MathSwitch           from '@/components/network-elements/elements/math-switch/math-switch.vue'
import MathMerge            from '@/components/network-elements/elements/math-merge/math-merge.vue'
import MathSoftmax          from '@/components/network-elements/elements/math-softmax/math-softmax.vue'
import MathSplit            from '@/components/network-elements/elements/math-split/math-split.vue'

import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/classic-ml-dbscans.vue'
import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/classic-ml-k-means.vue'
import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/classic-ml-k-nearest.vue'
import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/classic-ml-random-forest.vue'
import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/classic-ml-vector-machine.vue'

import LayerContainer       from '@/components/network-elements/elements/layer-container/layer-container.vue'
import LayerCustom          from '@/components/network-elements/elements/layer-custom/layer-custom.vue'

import SettingsArrow        from '@/components/network-elements/elements-settings/setting-arrow.vue'

import { mapGetters, mapMutations, mapActions } from 'vuex';
import { deepCopy } from "@/core/helpers.js";

export default {
  name: 'NetworkField',
  components: {
    DataData, DataEnvironment, DataRandom,
    // DataCloud,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape, ProcessRescale,
    // ProcessCrop,
    TrainNormal, TrainRegression, TrainGenetic, TrainDynamic, TrainReinforce, TrainDetector, TrainGan,
    // TrainLoss, TrainOptimizer, 
    MathArgmax, MathMerge, MathSoftmax, MathSwitch,
    // MathSplit,

    // ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,
    LayerContainer, LayerCustom,
    SettingsArrow
  },
  mounted() {
    this.drawArrows();
    //console.log(this.$refs.network);
    //this.SET_elementNetworkField({...this.$refs.network})
  },
  beforeDestroy() {
    this.removeArrowListener();
  },
  props: {
    scaleNet: {
      type: Number,
      default: 100,
    },
  },
  data() {
    return {
      settings: 'Data',
      arrowsList: [],
      resizeTimeout: null,
      layerSize: 60,
      offset: {
        offsetX: 0,
        offsetY: 0,
      },
      svgWidth: '100%',
      svgHeight: '100%',
      multiSelect: {
        show: false,
        xStart: 0,  yStart: 0,
        x: 0,       y: 0,
        width: 0,   height: 0
      },
      currentFocusedArrow: null,
      currentFocusedArrowData: null,
    }
  },
  computed: {
    ...mapGetters({
      tutorialActiveAction: 'mod_tutorials/getActiveAction',
      tutorialDottedArrow:  'mod_tutorials/getIsDottedArrow',
      currentNetwork:       'mod_workspace/GET_currentNetwork',
      canEditLayers:        'mod_workspace/GET_networkIsOpen',
      statisticsIsOpen:     'mod_workspace/GET_statisticsIsOpen',
      testingIsOpen:        'mod_workspace/GET_testIsOpen',
    }),
    isGridEnabled() {
      return false;
      return this.$store.state.globalView.isGridEnabled;
    },
    fullNetworkElementList() {
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
    },
    networkElementList() {
      let currentNetwork = this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
      let newNet = {};
      for(let id in currentNetwork) {
        let el = currentNetwork[id];
        if(!el.layerNone || el.componentName === 'LayerContainer') newNet[id] = el
      }
      return newNet
    },
    networkScale() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    hotKeyPressDelete() {
      return this.$store.state.mod_events.globalPressKey.del
    },
    eventCalcArrow() {
      return this.$store.state.mod_events.calcArray
    },
    preArrow() {
      return this.$store.state.mod_workspace.preArrow;
    },
    arrowStyle() {
      let width = `${this.networkScale  * 2}`;

      let style = {
        'strokeWidth': width,
      };

      return style;
    },
    styleSvgArrow() {
      const size = {
        width: this.svgWidth,
        height: this.svgHeight,
        zIndex: 1
      };
      return size
    },
    scaledLayerSize() {
      return this.layerSize * this.networkScale;
    }
  },
  watch: {
    statisticsIsOpen() {
      this.calcSvgSize()
    },
    networkScale(currentZoom, oldZoom) {
      this.positionZoomChange(currentZoom, oldZoom);
      this.calcSvgSize(true);
    },
    eventCalcArrow() {
      //this.tutorialPointActivate({way: 'next', validation: this.tutorialActiveAction.id});
      this.createArrowList()
    },
    hotKeyPressDelete() {
      this.deleteArrow()
    },
    '$store.state.mod_events.eventResize': {
      handler() {
        this.calcSvgSize()
      }
    },
  },
  methods: {
    ...mapMutations({
      change_singleElementPosition: 'mod_workspace/change_singleElementPosition',
      change_groupContainerDiff: 'mod_workspace/change_groupContainerDiff',
    }),
    ...mapActions({
      tutorialPointActivate:   'mod_tutorials/pointActivate',
      SET_elementNetworkField: 'mod_workspaceHelpers/SET_elementNetworkField',
      markAllUnselectedAction: 'mod_workspace/markAllUnselectedAction',
    }),
    refNetworkMouseDown(ev) {
      if(ev.target.nodeName === 'svg' && !(ev.shiftKey || ev.metaKey || ev.ctrlKey)) {
        this.markAllUnselectedAction();
      }
      const isLeftBtn = ev.buttons === 1;
      const isEditMode = this.networkMode === 'edit';
      const isOpenNet = this.canEditLayers;
      const targetEl = ev.target.nodeName === 'svg';

      if(isLeftBtn && isEditMode && isOpenNet && targetEl) {
        this.calcOffset();
        this.multiSelect.show = true;
        this.multiSelect.xStart = this.multiSelect.x = this.findXPosition(ev);
        this.multiSelect.yStart = this.multiSelect.y = this.findYPosition(ev);
        this.$refs.network.addEventListener('mousemove', this.moveMultiSelect);
        document.addEventListener('mouseup', this.mouseUpMultiSelect);
      }
      if(isLeftBtn && !isEditMode && isOpenNet && targetEl) {
        this.$store.dispatch('mod_workspace/SET_netMode', 'edit');
      }
    },
    moveMultiSelect(ev) {
      const xPosition = this.findXPosition(ev);
      const yPosition = this.findYPosition(ev);
      const xStart = this.multiSelect.xStart;
      const yStart = this.multiSelect.yStart;

      this.multiSelect.width =  Math.abs(xPosition - xStart);
      this.multiSelect.height = Math.abs(yPosition - yStart);

      if(xStart > xPosition) this.multiSelect.x = xPosition;
      if(yStart > yPosition) this.multiSelect.y = yPosition;
    },
    mouseUpMultiSelect() {
      const xStart = this.multiSelect.x;
      const yStart = this.multiSelect.y;
      const xStop = xStart + this.multiSelect.width - this.scaledLayerSize;
      const yStop = yStart + this.multiSelect.height - this.scaledLayerSize;

      for (var el in this.networkElementList) {
        const element = this.networkElementList[el];
        const x = element.layerMeta.position.left;
        const y = element.layerMeta.position.top;
        if(x > xStart
          && x < xStop
          && y > yStart
          && y < yStop ) {
          this.$store.dispatch('mod_workspace/SET_elementMultiSelect', { id: element.layerId, setValue: true });
        }
      }

      this.multiSelect = {
        show: false,
        xStart: 0,  yStart: 0,
        x: 0,       y: 0,
        width: 0,   height: 0,
      };

      this.removeMultiSelectListener();
      this.$refs.network.click();
    },
    removeMultiSelectListener() {
      this.$refs.network.removeEventListener('mousemove', this.moveMultiSelect);
      document.removeEventListener('mouseup', this.mouseUpMultiSelect);
    },
    // resizeCalc(ev) {
    //   let width = ev.srcElement.innerWidth;
    //   if(this.smallViewPort) {
    //     if(width > 1440) this.smallViewPort = false;
    //   }
    //   else {
    //     if(width <= 1440) this.smallViewPort = true;
    //   }
    // },
    calcOffset() {
      this.offset = {
       offsetX: this.$refs.network.parentElement.offsetLeft,
       offsetY: this.$refs.network.parentElement.offsetTop
      };
    },
    positionZoomChange(newScale, oldScale) {
      for (var el in this.fullNetworkElementList) {
        const element = this.fullNetworkElementList[el];
        const x0 = element.layerMeta.position.left;
        const y0 = element.layerMeta.position.top;

        this.change_singleElementPosition({
          id: el,
          top: y0 / oldScale * newScale,
          left: x0 / oldScale * newScale
        })

        if (element.layerMeta.containerDiff) {
          const preTop = element.layerMeta.containerDiff.top;
          const preLeft = element.layerMeta.containerDiff.left;
          this.change_groupContainerDiff({
            id: el,
            top: preTop / oldScale * newScale,
            left: preLeft / oldScale * newScale
          })
        }
      }
    },
    calcSvgSize(isZoomed) {
      const parentWorkspace = this.$parent.$refs.container;
      let offsetHeight = parentWorkspace.offsetHeight;
      let offsetWidth = parentWorkspace.offsetWidth;
      const gapSize = 60;
      
      // calculate max boundaries for network elements
      const positions = Object.values(this.networkElementList).map(item => item.layerMeta.position);
      const maxWidthPositions = Math.max(...positions.map(position => position.left)) + this.layerSize * this.networkScale + gapSize;
      const maxHeightPositions = Math.max(...positions.map(position => position.top)) + this.layerSize * this.networkScale + gapSize;

      this.svgWidth = Math.max(offsetWidth, maxWidthPositions);
      this.svgHeight = Math.max(offsetHeight, maxHeightPositions);

      if (isZoomed) {
        this.drawArrows();
        parentWorkspace.scrollLeft = 0;
        parentWorkspace.scrollTop = 0;
      }
    },

    //-------------
    //Arrow methods
    //--------------
    deleteArrow() {
      if(!this.canEditLayers || !this.currentFocusedArrow) return;

      let focusArray = this.currentFocusedArrow;
      let connection = {
        startID: focusArray.dataset.startid,
        stopID: focusArray.dataset.stopid,
      };
      this.$store.dispatch('mod_workspace/DELETE_arrow', connection);
      this.$store.dispatch('mod_api/API_getOutputDim');
      focusArray.blur();
      this.clearArrowFocus();
    },
    focusArrow(ev, arrow) {
      this.currentFocusedArrowData = arrow;
      this.currentFocusedArrow = ev.target;
    },
    blurArrow() {
      this.clearArrowFocus();
    },

    clearArrowFocus() {
      this.currentFocusedArrowData = null;
      this.currentFocusedArrow = null;
    },
    drawArrows() {
      this.calcOffset();
      //this.calcLayerSize();
      this.createArrowList();
    },
    addArrowListener() {
      this.$refs.network.addEventListener('mousemove', this.arrowMovePaint);
      document.addEventListener('mouseup', this.removeArrowListener);
    },
    arrowMovePaint(ev) {
      this.$store.commit('mod_tutorials/SET_isDottedArrow', false);
      ev.preventDefault();
      ev.stopPropagation();
      this.$store.commit('mod_workspace/SET_preArrowStop', {
        x: this.findXPosition(ev),
        y: this.findYPosition(ev)
      });
    },
    removeArrowListener() {
      this.$store.commit('mod_workspace/CLEAR_preArrow');
      this.$refs.network.removeEventListener('mousemove', this.arrowMovePaint);
      document.removeEventListener('mouseup', this.removeArrowListener)
    },
    createArrowList() {
      if(!this.networkElementList) {
        this.arrowsList = [];
        return;
      }

      this.calcSvgSize();
      const sizeEl = this.layerSize * this.networkScale;
      const connectList = [];
      const net = this.networkElementList;

      findPerspectiveSide();
      calcCorrectPosition();
      this.arrowsList = connectList;

      function findPerspectiveSide() {
        for (let elId in net) {
          net[elId].calcAnchor = { top: [], right: [], bottom: [], left: []};
        };

        for (let item in net) {
          const itemEl = net[item];
          if(itemEl.connectionArrow.length === 0) continue;
          for (var numEl in itemEl.connectionArrow) {
            let outEl = itemEl.connectionArrow[numEl];
            let newArrow = {
              l1: itemEl,
              l2: net[outEl],
              correctPosition: {
                start: { x: 0, y: 0 },
                stop:  { x: 0, y: 0 },
              }
            };
            if(!newArrow.l1 || !newArrow.l2 || newArrow.l1.layerNone || newArrow.l2.layerNone) continue;
            Object.defineProperty(newArrow, 'positionArrow', {
              get() {
                const x1 = this.l1.layerMeta.position.left + this.correctPosition.start.x;
                const y1 = this.l1.layerMeta.position.top + this.correctPosition.start.y;
                const x2 = this.l2.layerMeta.position.left + this.correctPosition.stop.x;
                const y2 = this.l2.layerMeta.position.top + this.correctPosition.stop.y;
                const path = calcArrowPath(x1, y1, x2, y2, this);
                return {path}
              },
              enumerable: true,
              configurable: false
            });
            findSideMinLength(newArrow.l1, newArrow.l2, newArrow);
            connectList.push(newArrow);
          }
        };
      }
      function findSideMinLength(l1, l2, currentEl) {
        let position = '';
        (l1.layerMeta.position.top <= l2.layerMeta.position.top)
          ? position = position + 'b'
          : position = position + 't';
        (l1.layerMeta.position.left <= l2.layerMeta.position.left)
          ? position = position + 'r'
          : position = position + 'l';

        switch(position) {
          case 'tr':
            let TRtop = topDot(l1);
            let TRright = rightDot(l1);
            let TRbottom = bottomDot(l2);
            let TRleft = leftDot(l2);
            let TRsides = calcMinLength(TRtop, TRright, TRbottom, TRleft);

            currentEl.sideStart = TRsides.start.side;
            currentEl.sideEnd = TRsides.end.side;
            l1.calcAnchor[TRsides.start.side].push(l2);
            l2.calcAnchor[TRsides.end.side].push(l1);
            break;

          case 'tl':
            let TLtop = topDot(l1);
            let TLleft = leftDot(l1);
            let TLbottom = bottomDot(l2);
            let TLright = rightDot(l2);
            let TLsides = calcMinLength(TLtop, TLleft, TLbottom, TLright);

            currentEl.sideStart = TLsides.start.side;
            currentEl.sideEnd = TLsides.end.side;
            l1.calcAnchor[TLsides.start.side].push(l2);
            l2.calcAnchor[TLsides.end.side].push(l1);
            break;

          case 'br':
            let BRbottom = bottomDot(l1);
            let BRright = rightDot(l1);
            let BRtop = topDot(l2);
            let BRleft = leftDot(l2);
            let BRsides = calcMinLength(BRbottom, BRright, BRtop, BRleft);
            currentEl.sideStart = BRsides.start.side;
            currentEl.sideEnd = BRsides.end.side;
            l1.calcAnchor[BRsides.start.side].push(l2);
            l2.calcAnchor[BRsides.end.side].push(l1);
            break;

          case 'bl':
            let BLbottom = bottomDot(l1);
            let BLleft = leftDot(l1);
            let BLtop = topDot(l2);
            let BLright = rightDot(l2);
            let BLsides = calcMinLength(BLbottom, BLleft, BLtop, BLright);

            currentEl.sideStart = BLsides.start.side;
            currentEl.sideEnd = BLsides.end.side;
            l1.calcAnchor[BLsides.start.side].push(l2);
            l2.calcAnchor[BLsides.end.side].push(l1);
            break
        }
        /* helpers position */
        function topDot(dot) {
          return {
            side: 'top',
            x: dot.layerMeta.position.left + (sizeEl / 2),
            y: dot.layerMeta.position.top
          }
        }
        function rightDot(dot) {
          return {
            side: 'right',
            x: dot.layerMeta.position.left + sizeEl,
            y: dot.layerMeta.position.top + (sizeEl / 2)
          }
        }
        function bottomDot(dot) {
          return {
            side: 'bottom',
            x: dot.layerMeta.position.left + (sizeEl / 2),
            y: dot.layerMeta.position.top + sizeEl
          }
        }
        function leftDot(dot) {
          return {
            side: 'left',
            x: dot.layerMeta.position.left,
            y: dot.layerMeta.position.top + (sizeEl / 2)
          }
        }
        /* END helpers position */
      }
      function calcMinLength(d1, d2, d3, d4) {
        const arrows = [
          { length: lengthLine(d1, d3), start: d1, end: d3 },
          { length: lengthLine(d1, d4), start: d1, end: d4 },
          { length: lengthLine(d2, d3), start: d2, end: d3 },
          { length: lengthLine(d2, d4), start: d2, end: d4 }
        ];
        return arrows.sort((a, b)=> a.length - b.length )[0];
      }
      function lengthLine(l1, l2) {
        return Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
      }
      function calcCorrectPosition() {
        connectList.forEach((itemEl, itemIndex, itemArr)=> {
          let currentLeftStart = itemEl.l2.layerMeta.position.left;
          let currentTopStart = itemEl.l2.layerMeta.position.top;
          let currentLeftEnd = itemEl.l1.layerMeta.position.left;
          let currentTopEnd = itemEl.l1.layerMeta.position.top;
          let indexSidePositionStart = '';
          let indexSidePositionEnd = '';
          let sideStartLength = itemEl.l1.calcAnchor[itemEl.sideStart].length;
          let sideEndLength = itemEl.l2.calcAnchor[itemEl.sideEnd].length;

          //calc start
          if(itemEl.sideStart === 'left' || itemEl.sideStart === 'right') {
            let sortVertSideStart = itemEl.l1.calcAnchor[itemEl.sideStart].sort(function(a, b) {
              return a.layerMeta.position.top - b.layerMeta.position.top;
            });
            indexSidePositionStart = sortVertSideStart.findIndex((element, index, array)=> {
              return element.layerMeta.position.top == currentTopStart;
            });
          }
          else {

            let sortGorSideStart = itemEl.l1.calcAnchor[itemEl.sideStart].sort(function(a, b) {
              return a.layerMeta.position.left - b.layerMeta.position.left;
            });
            indexSidePositionStart = sortGorSideStart.findIndex((element, index, array)=> {
              return element.layerMeta.position.left == currentLeftStart;
            });
          }
          itemEl.correctPosition.start = calcValuePosition(itemEl.sideStart, sideStartLength, indexSidePositionStart);
          //calc END
          if(itemEl.sideEnd === 'left' || itemEl.sideEnd === 'right') {
            let sortVertSideEnd = itemEl.l2.calcAnchor[itemEl.sideEnd].sort(function(a, b) {
              return a.layerMeta.position.top - b.layerMeta.position.top;
            });
            indexSidePositionEnd = sortVertSideEnd.findIndex((element, index, array)=> {
              return element.layerMeta.position.top == currentTopEnd;
            });
          }
          else {
            let sortGorSideEnd = itemEl.l2.calcAnchor[itemEl.sideEnd].sort(function(a, b) {
              return a.layerMeta.position.left - b.layerMeta.position.left;
            });
            indexSidePositionEnd = sortGorSideEnd.findIndex((element, index, array)=> {
              return element.layerMeta.position.left == currentLeftEnd;
            });
          }
          itemEl.correctPosition.stop = calcValuePosition(itemEl.sideEnd, sideEndLength, indexSidePositionEnd);
        })

      }
      function calcValuePosition(side, lengthSide, indexSide) {
        switch(side) {
          case 'top':
            return { x: (sizeEl / (lengthSide + 1)) * (indexSide + 1), y: 0 };
            break;
          case 'right':
            return { x: sizeEl, y: (sizeEl / (lengthSide + 1)) * (indexSide + 1) };
            break;
          case 'bottom':
            return { x: (sizeEl / (lengthSide + 1)) * (indexSide + 1), y: sizeEl };
            break;
          case 'left':
            return { x: 0, y: (sizeEl / (lengthSide + 1)) * (indexSide + 1) };
            break;
        }
      }
      function calcArrowPath(startX, startY, stopX, stopY, ctx) {
        const arrow = ctx;
        const vectorVal = 0.65;
        const vectorX = Math.round((stopX - startX) * vectorVal);
        const vectorY = Math.round((stopY - startY) * vectorVal);
        const pointStartX = arrow.sideStart === 'left' || arrow.sideStart === 'right'
          ? startX + vectorX
          : startX;
        const pointStartY = arrow.sideStart === 'top' || arrow.sideStart === 'bottom'
          ? startY + vectorY
          : startY;
        const pointStopX = arrow.sideEnd === 'left' || arrow.sideEnd === 'right'
          ? stopX - vectorX
          : stopX;
        const pointStopY = arrow.sideEnd === 'top' || arrow.sideEnd === 'bottom'
          ? stopY - vectorY
          : stopY;
        return {
          arrow: `M${startX},${startY}C${pointStartX},${pointStartY} ${pointStopX},${pointStopY} ${stopX},${stopY}`,
          settings: {
            x: calcHalfLength(startX, pointStartX, pointStopX, stopX),
            y: calcHalfLength(startY, pointStartY, pointStopY, stopY)
          }
        }
      }
      function calcHalfLength(dot1, dot2, dot3, dot4) {
        return 0.125 * dot1 + 0.375 * dot2 + 0.375 * dot3 + 0.125 * dot4;
      }
    },
    findXPosition(event) {
      const scrollPosition = document.querySelector('.js-info-section_main').scrollLeft;
      return (event.pageX - this.offset.offsetX + scrollPosition)
    },
    findYPosition(event) {
      const scrollPosition = document.querySelector('.js-info-section_main').scrollTop;
      return (event.pageY - this.offset.offsetY + scrollPosition)
    },
    getLastElementLegArrowData(arrow) {
      const isLayerTypeContainer = arrow.l1.layerType === 'Container';
      let arrowLeg1 = arrow.l1;
      if(isLayerTypeContainer) {
        // find id
        let keysOfContainerLayersListFrom = Object.keys(arrow.l1.containerLayersList);
        let keysOfContainerLayersListTo = arrow.l2.connectionIn;
        const keyOfLastElementFromGroup = keysOfContainerLayersListFrom.filter(value => keysOfContainerLayersListTo.includes(value))[0];
        if(keyOfLastElementFromGroup) {
          let currentNetworkElementList = this.fullNetworkElementList;
          arrowLeg1 = currentNetworkElementList[keyOfLastElementFromGroup]; 
        }
      }
      return arrowLeg1;
    },
    arrowClassStyle(arrow) {
      const arrowLine1 = this.getLastElementLegArrowData(arrow);

      let result = [];
      if (arrowLine1.layerMeta.isInvisible || arrow.l2.layerMeta.isInvisible) {
        result.push('arrow--hidden');
      }
      if (!arrowLine1.layerMeta.OutputDim || arrowLine1.layerCodeError) {
        result.push('svg-arrow_line--empty');
      }

      if(this.currentFocusedArrowData === arrow) {
        result.push('is-focused');
      }
      return result;
    },
    arrowMarkerStyle(arrow) {
      const arrowLine1 = this.getLastElementLegArrowData(arrow);

      return (!arrowLine1.layerMeta.OutputDim || arrowLine1.layerCodeError)
        ? 'url(#svg-arrow_triangle-empty)'
        : 'url(#svg-arrow_triangle)';
    },
  }
}
