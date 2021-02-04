import DataData             from '@/components/network-elements/elements/data-data/data-data.vue'
import DataEnvironment      from '@/components/network-elements/elements/data-environment/data-environment.vue'
import DataCloud            from '@/components/network-elements/elements/data-cloud/data-cloud.vue'
import DataRandom           from '@/components/network-elements/elements/data-random/data-random.vue'
import IoInput          from '@/components/network-elements/elements/io-input/io-input.vue'

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

import NetworkDrag    from '@/components/network-field/network-drag.js'
import NetworkGrid    from '@/components/network-field/network-grid.vue'
import { mapGetters, mapMutations, mapActions } from 'vuex';
import { deepCopy } from "@/core/helpers.js";

let resizeObservable = null;

export default {
  name: 'NetworkField',
  components: {
    DataData, DataEnvironment, DataRandom, IoInput,
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
    SettingsArrow,
    NetworkGrid
  },
  mixins: [NetworkDrag],
  mounted() {
    this.drawArrows();
    if(!this.isViewMode) {
      this.$store.dispatch('mod_events/EVENT_IOGenerateAction', null, {root: true})
        .then(() => {
          const networkID = this.currentNetwork.networkID;
          if(!this.fetchedPreviewsNetworksIds.includes(networkID)) {
            this.getAllPreviews();
            this.$store.commit("mod_workspace/setFetchedPreviewsNetworksIds", networkID);
          }
        });
    }

    this.lunchTheResizeObserver();
    setTimeout(this.calculateGridStyle(),0);

  },
  beforeDestroy() {
    resizeObservable.disconnect();
    this.removeArrowListener();
  },
  props: {
    scaleNet: {
      type: Number,
      default: 100,
    },
    isViewMode: {
      type: Boolean,
      default: false,
    }
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
      svgWidth: null,
      svgHeight: null,
      multiSelect: {
        show: false,
        xStart: 0,  yStart: 0,
        x: 0,       y: 0,
        width: 0,   height: 0
      },
      currentFocusedArrow: null,
      currentFocusedArrowData: null,
      mouseOutsideDirection: '',
      gridStyle: {},
      resizeObservable: null,
    }
  },
  computed: {
    ...mapGetters({
      viewType:               'mod_workspace/GET_viewType',
      currentNetwork:         'mod_workspace/GET_currentNetwork',
      canEditLayers:          'mod_workspace/GET_networkIsOpen',
      statisticsIsOpen:       'mod_workspace/GET_statisticsIsOpen',
      testingIsOpen:          'mod_workspace/GET_testIsOpen',
      statisticsOrTestIsOpen: 'mod_workspace/GET_statisticsOrTestIsOpen',
      getCurrentStepCode:     'mod_tutorials/getCurrentStepCode',
      getIsWorkspaceDragEvent: 'mod_events/getIsWorkspaceDragEvent',
    }),
    fetchedPreviewsNetworksIds() {
      return this.$store.state.mod_workspace.fetchedPreviewsNetworksIds;
    },
    isGridEnabled() {
      return this.$store.state.globalView.isGridEnabled;
    },
    networkElementListSnapshot() {
      return this.$store.getters['mod_workspace/GET_currentNetworkSnapshotElementList'];
    },
    fullNetworkElementList() {
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
    },
    computedFullNetworkElementList() {
      return Object.assign({}, this.fullNetworkElementList);
    },
    networkElementList() {
      let currentNetworkElementList = this.statisticsOrTestIsOpen
        ? this.networkElementListSnapshot
        : this.fullNetworkElementList;

      let newNet = {};
      let selectedOne = false;

      for(let id in currentNetworkElementList) {
        let el = currentNetworkElementList[id];
        if(this.statisticsOrTestIsOpen) {
          el.layerMeta.isSelected = false;
          if (el.layerType==="Training") {
            el.layerMeta.isSelected = true;
          } else {
            if (!selectedOne) {
              el.layerMeta.isSelected = true;
              selectedOne = true;
            }
          }
        }
        if(!el.layerNone || el.componentName === 'LayerContainer') newNet[id] = el
      }
      return newNet
    },
    networkScale() {
      return this.$store.getters['mod_workspace/GET_currentNetworkZoom'];
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
    // eventIOGenerate() {
    //   return this.$store.state.mod_events.eventIOGenerate
    // },
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
        zIndex: 6,
        overflow: 'visible'
      };
      return size
    },
    scaledLayerSize() {
      return this.layerSize * this.networkScale;
    },
    inComponentDrop() {
      return this.$store.state['mod_events'].componentEvents.model.componentDrop;
    }
  },
  watch: {
    inComponentDrop(){
      setTimeout(() => {
        this.calcSvgSize();
        this.calculateGridStyle();
      }, 0)
    },
    statisticsOrTestIsOpen() {
      this.calcSvgSize(true)
    },
    networkScale(currentZoom, oldZoom) {
      this.calcSvgSize(true);
      this.calculateGridStyle();
      setTimeout(()=> this.createArrowList(), 0);
    },
    eventCalcArrow() {
      this.createArrowList()
    },
    hotKeyPressDelete() {
      this.deleteArrow()
    },
    '$store.state.mod_events.eventResize': {
      handler() {
        this.calculateGridStyle();
        this.calcSvgSize();
      }
    },
    computedFullNetworkElementList: {
      handler(newVal, oldVal) {

        if (this.getCurrentStepCode !== 'tutorial-workspace-layer-data') {
          return;
        }

        const newKeys = newVal ? Object.keys(newVal) : [];
        const oldKeys = oldVal ? Object.keys(oldVal) : [];

        if (newVal && 
          oldVal &&
          newKeys.length === oldKeys.length + 1) {
            this.setNextStep({currentStep:'tutorial-workspace-layer-data'});
        }
      }
    }

    // eventIOGenerate() {
    //   this.generateForwardAndBackwardConnections();
    // }
  },
  methods: {
    ...mapMutations({
      change_singleElementPosition:           'mod_workspace/change_singleElementPosition',
      change_singleElementInSnapshotPosition: 'mod_workspace/change_singleElementInSnapshotPosition',
      change_groupContainerDiff:              'mod_workspace/change_groupContainerDiff',
    }),
    ...mapActions({
      SET_elementNetworkField: 'mod_workspaceHelpers/SET_elementNetworkField',
      markAllUnselectedAction: 'mod_workspace/markAllUnselectedAction',
      unselectElements:        'mod_workspace/SET_elementUnselect',
      setNextStep:             'mod_tutorials/setNextStep',
      layerAddedAction:        'mod_tutorials/tutorial-workspace-layer-added-setup',
    }),
    getElSize(layerId) {
      const el = document.querySelector(`[layer-id="${layerId}"]`);
      const width = el.offsetWidth * this.networkScale;
      const height = el.offsetHeight * this.networkScale;
      return {
        width,
        height
      }
     },
    refNetworkMouseDown(ev) {
      if(ev.target.className === 'network-field' && !(ev.shiftKey || ev.metaKey || ev.ctrlKey)) {
        this.markAllUnselectedAction();
      }
      const isLeftBtn = ev.buttons === 1;
      const isEditMode = this.networkMode === 'edit';
      const isOpenNet = this.canEditLayers;
      const targetEl = ev.target.className === 'network-field';

      if(isLeftBtn && isEditMode && isOpenNet && targetEl) {
        this.calcOffset();
        this.multiSelect.show = true;
        this.multiSelect.xStart = this.multiSelect.x = this.findXPosition(ev);
        this.multiSelect.yStart = this.multiSelect.y = this.findYPosition(ev);
        this.$refs.network.addEventListener('mousemove', this.moveMultiSelect);
        document.addEventListener('mouseout', this.handleMultiselectToolOutsideNetwork)
        document.addEventListener('mousemove', this.handleSelectToolMouseOutsideNetwork)
        document.addEventListener('mouseup', this.mouseUpMultiSelect);
      }
      if(isLeftBtn && !isEditMode && isOpenNet && targetEl) {
        this.$store.dispatch('mod_workspace/SET_netMode', 'edit');
      }
    },
    handleSelectToolMouseOutsideNetwork(ev) {
      const { mouseOutsideDirection } = this;
      if(mouseOutsideDirection !== '') {
        var el = document.getElementById('networkWorkspace');
        const moveSpace = 10;
        isOnSide('r', mouseOutsideDirection) && (el.scrollLeft += moveSpace)
        isOnSide('l', mouseOutsideDirection) && (el.scrollLeft -= moveSpace)
        isOnSide('t', mouseOutsideDirection) && (el.scrollTop -= moveSpace)
        isOnSide('b', mouseOutsideDirection) && (el.scrollTop += moveSpace)
        
        this.moveMultiSelect(ev);
      }

      function isOnSide(sideChar, str) {
        return str.indexOf(sideChar) !== -1
      }
    },
    handleMultiselectToolOutsideNetwork(mouseEvent) {
      this.mouseOutsideDirection = '';
      const elemBounding = document.getElementById('networkWorkspace').getBoundingClientRect();
      const elementLeftEdge = elemBounding.left;
      const elementTopEdge = elemBounding.top;
      const elementRightEdge = elemBounding.right;
      const elementBottomEdge = elemBounding.bottom;
      const mouseX = mouseEvent.pageX;
      const mouseY = mouseEvent.pageY;

      mouseY >= elementBottomEdge && (this.mouseOutsideDirection += 'b')
      mouseY <= elementTopEdge && (this.mouseOutsideDirection += 't')
      mouseX >= elementRightEdge && (this.mouseOutsideDirection += 'r')
      mouseX <= elementLeftEdge && (this.mouseOutsideDirection += 'l')
    },
    moveMultiSelect(ev) {
      if(this.getIsWorkspaceDragEvent) { 
        this.mouseUpMultiSelect();
        return 0 
      };
      const xPosition = this.findXPosition(ev);
      const yPosition = this.findYPosition(ev);
      const xStart = this.multiSelect.xStart;
      const yStart = this.multiSelect.yStart;

      this.multiSelect.width =  Math.abs(xPosition - xStart);
      this.multiSelect.height = Math.abs(yPosition - yStart);

      if(xStart > xPosition) this.multiSelect.x = xPosition;
      if(yStart > yPosition) this.multiSelect.y = yPosition;

      for (var el in this.networkElementList) {

        if(this.isElementHoveredBySelectingTool(el)) {
          document.querySelector(`[layer-id="${el}"]`).classList.add('net-element--selecting')
        } else {
          document.querySelector(`[layer-id="${el}"]`).classList.remove('net-element--selecting')
        }
      }
    },
    mouseUpMultiSelect() {
    
      for (var el in this.networkElementList) {
        if(this.isElementHoveredBySelectingTool(el)) {
          document.querySelector(`[layer-id="${el}"]`).classList.remove('net-element--selecting')
          this.$store.dispatch('mod_workspace/SET_elementMultiSelect', { id: this.networkElementList[el].layerId, setValue: true });
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
    isElementHoveredBySelectingTool(el) {
      const element = this.networkElementList[el];
      const elSize = this.getElSize(el);

      const x = element.layerMeta.position.left;
      const y = element.layerMeta.position.top;
      const x1 = element.layerMeta.position.left + elSize.width;
      const y1 = element.layerMeta.position.top + elSize.height;
      
      const tempX = [this.multiSelect.x, this.multiSelect.width + this.multiSelect.x].sort((a, b) => (a - b));
      const tempY = [this.multiSelect.y, this.multiSelect.height + this.multiSelect.y].sort((a, b) => (a - b));
      
      const xStart = tempX[0];
      const yStart = tempY[0];
      const xEnd = tempX[1];
      const yEnd = tempY[1];
 
      const rect = [xStart, xEnd, yStart, yEnd];
      const rectEl = [x, x1, y, y1];

      if(
        this.isPointInsideRect(x, y, rect)
        || this.isPointInsideRect(x1, y, rect)
        || this.isPointInsideRect(x, y1, rect)
        || this.isPointInsideRect(x1, y1, rect)
        || this.isPointInsideRect(xStart, yStart, rectEl)
        || this.isPointInsideRect(xEnd, yStart, rectEl)
        || this.isPointInsideRect(xStart, yEnd, rectEl)
        || this.isPointInsideRect(xEnd, yEnd, rectEl)
      ) {
        return true;
      } else {
        return false;
      }
    },
    isPointInsideRect(x, y, rect) {

      if((x > rect[0]) && (x < rect[1])
      && (y > rect[2]) && (y < rect[3])) {
        return true;
      }
      return false;
    },
    removeMultiSelectListener() {
      this.$refs.network.removeEventListener('mousemove', this.moveMultiSelect);
      document.removeEventListener('mouseup', this.mouseUpMultiSelect);
      document.removeEventListener('mouseout', this.handleMultiselectToolOutsideNetwork)
      document.removeEventListener('mousemove', this.handleSelectToolMouseOutsideNetwork)
      this.mouseOutsideDirection = '';
    },
    calcOffset() {
      this.offset = {
       offsetX: this.$refs.network.parentElement.parentElement.parentElement.offsetLeft,
       offsetY: this.$refs.network.parentElement.parentElement.parentElement.offsetTop
      };
    },
    calcSvgSize(redrawArrows) {
      const parentWorkspace = this.$parent.$refs.container;
      if(!parentWorkspace) { return 0} 
      let offsetHeight = parentWorkspace.offsetHeight;
      let offsetWidth = parentWorkspace.offsetWidth;
      const gapSizeWidth = 145 * this.networkScale;
      const gapSizeHeight = 223  * this.networkScale;
      // calculate max boundaries for network elements
      const positions = Object.values(this.networkElementList).map(item => item.layerMeta.position);
      const maxWidthPositions = Math.max(...positions.map(position => position.left)) + this.layerSize * this.networkScale + gapSizeWidth;
      const maxHeightPositions = Math.max(...positions.map(position => position.top)) + this.layerSize * this.networkScale + gapSizeHeight;
      this.svgWidth = Math.max(offsetWidth, maxWidthPositions) + 'px';
      this.svgHeight = Math.max(offsetHeight, maxHeightPositions) + 'px';

      if (redrawArrows) {
        this.$nextTick(() => {
          this.drawArrows();
          parentWorkspace.scrollLeft = 0;
          parentWorkspace.scrollTop = 0;
        });
      }
    },

    //-------------
    //Arrow methods
    //--------------
    deleteArrow() {
      if(!this.canEditLayers || !this.currentFocusedArrow) return;
      let focusArray = this.currentFocusedArrow;
      const arrowData = this.currentFocusedArrowData;
      let connection = {
        startIds: arrowData.startIds,
        stopIds: arrowData.stopIds,
      };

      let startDot = document.querySelector(`[data-output-circle-dot-id="${arrowData.startIds.variable}"][data-output-layer-id="${arrowData.startIds.layer}"]`);
      startDot.classList.remove("connect");
      let stopDot = document.querySelector(`[data-input-circle-dot-id="${arrowData.stopIds.variable}"][data-input-layer-id="${arrowData.stopIds.layer}"]`);
      stopDot.classList.remove("connect");

      this.$store.dispatch('mod_workspace/DELETE_arrow', connection)
        .then(() => {
          this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', connection.stopIds.layer);
        });
      this.$store.dispatch('mod_api/API_getOutputDim');
      focusArray.blur();
      this.clearArrowFocus();
    },
    focusArrow(ev, arrow) {
      this.unselectElements();
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
      this.calculateGridStyle();
    },
    addArrowListener() {
      this.$refs.network.addEventListener('mousemove', this.arrowMovePaint);
      document.addEventListener('mouseup', this.removeArrowListener);
    },
    arrowMovePaint(ev) {
      // 4
      // this.$store.commit('mod_tutorials/SET_isDottedArrow', false);
      ev.preventDefault();
      ev.stopPropagation();
      this.$store.commit('mod_workspace/SET_preArrowStop', {
        x: this.findXPosition(ev),
        y: this.findYPosition(ev)
      });
    },
    removeArrowListener() {
      // 5
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

      this.$nextTick(() => {
        findPerspectiveSide(this.networkScale);
        // calcCorrectPosition(this.networkScale);
        this.arrowsList = connectList;
      })

      function findPerspectiveSide(zoom) {
        const validConnectionIds = [];

         for (let elId in net) {
          net[elId].calcAnchor = { top: [], right: [], bottom: [], left: []};
        };
        for (let elId in net) {
          const el = net[elId];

          // Data* layers have no inputs
          if (!el.inputs) { return; }

          Object.keys(el.inputs).map(keyId => {
            if(el.inputs[keyId].reference_var_id !== null) {
              let newArrow = {
                l1: net[el.inputs[keyId].reference_layer_id],
                l2: net[elId],
                correctPosition: {
                  start: { x: 0, y: 0 },
                  stop:  { x: 0, y: 0 },
                },
                startIds: {
                  layer: el.inputs[keyId].reference_layer_id,
                  variable: el.inputs[keyId].reference_var_id,
                },
                stopIds: {
                  layer: elId,
                  variable: keyId
                }
              };
              Object.defineProperty(newArrow, 'positionArrow', {
                get() {
                  
                  // get start dot position
                  let startElement = document.querySelector(`[layer-id="${newArrow.startIds.layer}"]`);
                  let startDot = document.querySelector(`[data-output-circle-dot-id="${newArrow.startIds.variable}"][data-output-layer-id="${newArrow.startIds.layer}"]`);
                  startDot.classList.add("connect");

                  const { x: startLayerX, y: startLayerY } = startElement.getBoundingClientRect();
                  const { x: startDotX, y: startDotY } = startDot.getBoundingClientRect();
                  const startDotPositionWidth = (startDotX - startLayerX);
                  const StartDotPositionHeight = (startDotY  - startLayerY) ;

                  //get stop dot position
                  let stopElement = document.querySelector(`[layer-id="${newArrow.stopIds.layer}"]`);
                  let stopDot = document.querySelector(`[data-input-circle-dot-id="${newArrow.stopIds.variable}"][data-input-layer-id="${newArrow.stopIds.layer}"]`);
                  stopDot.classList.add("connect");
                  
                  const { x: stopLayerX, y: stopLayerY } = stopElement.getBoundingClientRect();
                  const { x: stopDotX, y: stopDotY } = stopDot.getBoundingClientRect();

                  const stopDotPositionWidth = (stopDotX - stopLayerX);
                  const stopDotPositionHeight = (stopDotY  - stopLayerY);

                  const x1 = this.l1.layerMeta.position.left + startDotPositionWidth + (3 * zoom);
                  const y1 = this.l1.layerMeta.position.top + StartDotPositionHeight + (3 * zoom);
                  const x2 = this.l2.layerMeta.position.left + stopDotPositionWidth + (3 * zoom);
                  const y2 = this.l2.layerMeta.position.top + stopDotPositionHeight + (3 * zoom);

                  const path = calcArrowPath(x1, y1, x2, y2, this);
                  
                  return {path}
                },
                enumerable: true,
                configurable: false
              });
              findSideMinLength(newArrow.l1, newArrow.l2, newArrow);
              connectList.push(newArrow);
            }
          })

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

          let currentNetworkElementList = this.statisticsOrTestIsOpen
            ? this.networkElementListSnapshot
            : this.fullNetworkElementList;
        
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
    getAllPreviews() {
      if (this.viewType !== 'model') { return; }

      let payload = {};
      for(let id in this.fullNetworkElementList) {
        const el = this.fullNetworkElementList[id];
        payload[id] = el.previewVariable;
      }
      this.$store.dispatch('mod_api/API_getBatchPreviewSample', payload);
    },
    calculateGridStyle() {
      let widthHeightStyle = {};
      if(this.$refs.network) {
        const clientWidth = this.$refs.network.clientWidth;
        const clientHeight = this.$refs.network.clientHeight;
        const width = (clientWidth / (this.networkScale * 100)) * 100
        const height = (clientHeight / (this.networkScale * 100)) * 100
        widthHeightStyle['width'] = width + 'px'
        widthHeightStyle['height'] = height + 'px'
      }
      this.gridStyle = {
        position: 'absolute',
        top: '0',
        left: '0',
        transform: `scale(${this.networkScale}`,
        transformOrigin: '0 0',
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        ...widthHeightStyle
      }
    },
    lunchTheResizeObserver() {
      resizeObservable = new ResizeObserver(() => {
        this.calcSvgSize(true)
        this.calculateGridStyle();
      })
  
      const elementThatShouldBeWatched = document.getElementById('networkWorkspace');
      resizeObservable.observe(elementThatShouldBeWatched);
    }
  },
}
