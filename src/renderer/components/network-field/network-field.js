import IoInput              from '@/components/network-elements/elements/io-input/io-input.vue'
  import IoOutputBackprop     from '@/components/network-elements/elements/io-output-backpropagation/io-output-backpropagation.vue'
  import IoOutputGenetic      from '@/components/network-elements/elements/io-output-genetic-algorithm/io-output-genetic-algorithm.vue'
  import IoOutputRouting      from '@/components/network-elements/elements/io-output-routing-algorithm/io-output-routing-algorithm.vue'

  import DataData             from '@/components/network-elements/elements/data-data/data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment/data-environment.vue'

  import DeepLearningFC       from '@/components/network-elements/elements/deep-learning-fc/deep-learning-fc.vue'
  import DeepLearningConv     from '@/components/network-elements/elements/deep-learning-conv/deep-learning-conv.vue'
  import DeepLearningDeconv   from '@/components/network-elements/elements/deep-learning-deconv/deep-learning-deconv.vue'
  import DeepLearningRecurrent from '@/components/network-elements/elements/deep-learning-recurrent/deep-learning-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop/process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed/process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale/process-grayscale.vue'
  import ProcessOneHot        from '@/components/network-elements/elements/process-one-hot/process-one-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape/process-reshape.vue'

  import TrainNormal          from '@/components/network-elements/elements/train-normal/train-normal.vue'
  import TrainNormalData      from '@/components/network-elements/elements/train-normal-data/train-normal-data.vue'
  import TrainGenetic         from '@/components/network-elements/elements/train-genetic/train-genetic.vue'
  import TrainDynamic         from '@/components/network-elements/elements/train-dynamic/train-dynamic.vue'
  import TrainReinforce       from '@/components/network-elements/elements/train-reinforce/train-reinforce.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax/math-argmax.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge/math-merge.vue'
  import MathSoftmax          from '@/components/network-elements/elements/math-softmax/math-softmax.vue'
  import MathSplit            from '@/components/network-elements/elements/math-split/math-split.vue'

  import ClassicMLDbscans     from '@/components/network-elements/elements/classic-ml-dbscans/classic-ml-dbscans.vue'
  import ClassicMLKMeans      from '@/components/network-elements/elements/classic-ml-k-means/classic-ml-k-means.vue'
  import ClassicMLKNN         from '@/components/network-elements/elements/classic-ml-k-nearest/classic-ml-k-nearest.vue'
  import ClassicMLRandomForest from '@/components/network-elements/elements/classic-ml-random-forest/classic-ml-random-forest.vue'
  import ClassicMLSVM         from '@/components/network-elements/elements/classic-ml-vector-machine/classic-ml-vector-machine.vue'

  import LayerContainer       from '@/components/network-elements/elements/layer-container/view-layer-container.vue'
  import { mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: 'NetworkField',
  components: {
    IoInput, IoOutputBackprop, IoOutputGenetic, IoOutputRouting,
    DataData, DataEnvironment,
    DeepLearningFC, DeepLearningConv, DeepLearningDeconv, DeepLearningRecurrent,
    ProcessCrop, ProcessEmbed, ProcessGrayscale, ProcessOneHot, ProcessReshape,
    TrainNormal, TrainNormalData, TrainGenetic, TrainDynamic, TrainReinforce,
    MathArgmax, MathMerge, MathSoftmax, MathSplit,
    ClassicMLDbscans, ClassicMLKMeans, ClassicMLKNN, ClassicMLRandomForest, ClassicMLSVM,
    LayerContainer
  },
  props: ['netIndex'],
  data() {
    return {
      settings: 'Data',
      arrowsList: [],
      resizeTimeout: null,
      layerSize: 52,
      smallViewPort: true,
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
      currentFocusedArrow: null
    }
  },
  mounted() {
    this.calcViewPort(true);
    window.addEventListener("resize", this.resizeCalc, false);
  },
  beforeDestroy() {
    this.removeArrowListener();
    window.removeEventListener("resize", this.resizeCalc, false);
  },
  computed: {
    ...mapGetters({
      tutorialActiveAction: 'mod_tutorials/getActiveAction',
      networkElementList: 'mod_workspace/GET_currentNetworkElementList',
      canEditLayers: 'mod_workspace/GET_networkCanEditLayers'
    }),
    networkScale() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    hotKeyPressDelete() {
      return this.$store.state.mod_events.globalPressKey.del
    },
    // networkElementList() {
    //   return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
    // },
    currentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
    statisticsIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openStatistics
    },
    testingIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
    },
    eventCalcArrow() {
      return this.$store.state.mod_events.calcArray
    },
    preArrow() {
      return this.$store.state.mod_workspace.preArrow;
    },
    styleSvgArrow() {
      return {
        width: this.svgWidth,
        height: this.svgHeight,
      }
    },
  },
  watch: {
    statisticsIsOpen() {
      this.calcSvgSize()
    },
    networkScale() {
      this.calcSvgSize()
    },
    eventCalcArrow() {
      this.tutorialPointActivate({way: 'next', validation: this.tutorialActiveAction.id});
      this.createArrowList()
    },
    smallViewPort() {
      this.drawArrows();
    },
    hotKeyPressDelete() {
      this.deleteArrow()
    },
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    refNetworkMouseDown(ev) {
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
        this.$refs.network.addEventListener('mouseup', this.removeMultiSelectListener);
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
    removeMultiSelectListener() {
      const xStart = this.multiSelect.x;
      const yStart = this.multiSelect.y;
      const xStop = xStart + this.multiSelect.width - this.layerSize;
      const yStop = yStart + this.multiSelect.height - this.layerSize;

      this.networkElementList.forEach((element, index)=> {
        const x = element.layerMeta.left;
        const y = element.layerMeta.top;
        if(x > xStart
          && x < xStop
          && y > yStart
          && y < yStop ) {
          this.$store.dispatch('mod_workspace/SET_elementMultiSelect', { path: [index], setValue: true });
        }
      });

      this.multiSelect = {
        show: false,
        xStart: 0,  yStart: 0,
        x: 0,       y: 0,
        width: 0,   height: 0,
      };
      this.$refs.network.removeEventListener('mousemove', this.moveMultiSelect);
      this.$refs.network.removeEventListener('mouseup', this.removeMultiSelectListener);
    },
    resizeCalc(ev) {
      let width = ev.srcElement.innerWidth;
      if(this.smallViewPort) {
        if(width > 1440) this.smallViewPort = false;
      }
      else {
        if(width <= 1440) this.smallViewPort = true;
      }
    },
    calcOffset() {
      this.offset = {
       offsetX: this.$refs.network.parentElement.offsetLeft,
       offsetY: this.$refs.network.parentElement.offsetTop
      };
    },
    calcLayerSize() {
      if(this.networkElementList.length) {
        this.layerSize = this.$refs.layer[0].$el.offsetWidth;
      }
    },
    calcViewPort(needCalcArray) {
      window.innerWidth > 1440 ? this.smallViewPort = false : this.smallViewPort = true;
      if(!this.smallViewPort) this.layerSize = 72;
      if(needCalcArray) this.drawArrows();
    },
    calcSvgSize() {
      let scrollHeight = this.$refs.network.scrollHeight;
      let scrollWidth = this.$refs.network.scrollWidth;
      let offsetHeight = this.$refs.network.offsetHeight;
      let offsetWidth = this.$refs.network.offsetWidth;
      scrollHeight > offsetHeight
        ? this.svgHeight = scrollHeight + 'px'
        : this.svgHeight = '100%';
      scrollWidth > offsetWidth
        ? this.svgWidth = scrollWidth + 'px'
        : this.svgWidth = '100%';

    },
    //-------------
    //Arrow methods
    //--------------
    deleteArrow() {
      if(this.statisticsIsOpen || this.testingIsOpen || !this.currentFocusedArrow) return;
      let focusArray = this.currentFocusedArrow;
      let connection = {
        startID: focusArray.dataset.startid,
        stopID: focusArray.dataset.stopid,
      };
      this.$store.dispatch('mod_workspace/DELETE_arrow', connection);
      this.$store.dispatch('mod_api/API_getOutputDim');
      focusArray.blur();
      this.currentFocusedArrow = null;
    },
    focusArrow(ev) {
      this.currentFocusedArrow = ev.target;
    },
    drawArrows() {
      this.calcOffset();
      this.calcLayerSize();
      this.createArrowList();
    },
    addArrowListener() {
      this.$refs.network.addEventListener('mousemove', this.arrowMovePaint);
      this.$refs.network.addEventListener('mouseup', this.removeArrowListener);
    },
    arrowMovePaint(ev) {
      ev.preventDefault();
      ev.stopPropagation();
      this.$store.commit('mod_workspace/SET_preArrowStop', {
        x: this.findXPosition(ev),
        y: this.findYPosition(ev)
      })
    },
    removeArrowListener() {
      this.$store.commit('mod_workspace/CLEAR_preArrow');
      this.$refs.network.removeEventListener('mousemove', this.arrowMovePaint);
      this.$refs.network.removeEventListener('mouseup', this.removeArrowListener)
    },
    createArrowList() {
      if(!this.networkElementList.length) return;
      this.calcSvgSize();
      
      const size = this.layerSize;
      const listID = {};
      const connectList = [];
      const net = this.networkElementList;
      findAllID();
      findPerspectiveSide();
      calcCorrectPosition();

      function findAllID() {
        net.forEach((itemEl, indexEl, arrNet)=> {
         let itemID = itemEl.layerId;
         itemEl.calcAnchor = { top: [], right: [], bottom: [], left: []};
         listID[itemID] = itemEl;
        });
      }
      function findPerspectiveSide() {
        net.forEach((itemEl, indexEl, arrNet)=> {
          if(itemEl.connectionOut.length === 0) return;
          for (var numEl in itemEl.connectionOut) {
            let outEl = itemEl.connectionOut[numEl];
            let newArrow = {
              l1: itemEl,
              l2: listID[outEl],
              correctPosition: {
                start: {
                  x: 0,
                  y: 0,
                },
                stop: {
                  x: 0,
                  y: 0,
                },
              }
            };
            Object.defineProperty(newArrow, 'positionArrow', {
              get() {
                const x1 = this.l1.layerMeta.left + this.correctPosition.start.x;
                const y1 = this.l1.layerMeta.top + this.correctPosition.start.y;
                const x2 = this.l2.layerMeta.left + this.correctPosition.stop.x;
                const y2 = this.l2.layerMeta.top + this.correctPosition.stop.y;
                const path = calcArrowPath(x1, y1, x2, y2, this);
                return {path}
              },
              enumerable: true,
              configurable: false
            });
            findSideMinLength(newArrow.l1, newArrow.l2, newArrow);
            connectList.push(newArrow);
          }
        });
      }
      function findSideMinLength(l1, l2, currentEl) {
        let position = '';
        (l1.layerMeta.top <= l2.layerMeta.top)
          ? position = position + 'b'
          : position = position + 't';
        (l1.layerMeta.left <= l2.layerMeta.left)
          ? position = position + 'r'
          : position = position + 'l';

        function topDot(dot) {
          return {
            side: 'top',
            x: dot.layerMeta.left + (size / 2),
            y: dot.layerMeta.top
          }
        }
        function rightDot(dot) {
          return {
            side: 'right',
            x: dot.layerMeta.left + size,
            y: dot.layerMeta.top + (size / 2)
          }
        }
        function bottomDot(dot) {
          return {
            side: 'bottom',
            x: dot.layerMeta.left + (size / 2),
            y: dot.layerMeta.top + size
          }
        }
        function leftDot(dot) {
          return {
            side: 'left',
            x: dot.layerMeta.left,
            y: dot.layerMeta.top + (size / 2)
          }
        }

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
          let currentLeftStart = itemEl.l2.layerMeta.left;
          let currentTopStart = itemEl.l2.layerMeta.top;
          let currentLeftEnd = itemEl.l1.layerMeta.left;
          let currentTopEnd = itemEl.l1.layerMeta.top;
          let indexSidePositionStart = '';
          let indexSidePositionEnd = '';
          let sideStartLength = itemEl.l1.calcAnchor[itemEl.sideStart].length;
          let sideEndLength = itemEl.l2.calcAnchor[itemEl.sideEnd].length;

          //calc start
          if(itemEl.sideStart === 'left' || itemEl.sideStart === 'right') {
            let sortVertSideStart = itemEl.l1.calcAnchor[itemEl.sideStart].sort(function(a, b) {
              return a.layerMeta.top - b.layerMeta.top;
            });
            indexSidePositionStart = sortVertSideStart.findIndex((element, index, array)=> {
              return element.layerMeta.top == currentTopStart;
            });
          }
          else {
           
            let sortGorSideStart = itemEl.l1.calcAnchor[itemEl.sideStart].sort(function(a, b) {
              return a.layerMeta.left - b.layerMeta.left;
            });
            indexSidePositionStart = sortGorSideStart.findIndex((element, index, array)=> {
              return element.layerMeta.left == currentLeftStart;
            });
          }
          itemEl.correctPosition.start = calcValuePosition(itemEl.sideStart, sideStartLength, indexSidePositionStart);
          //calc END
          if(itemEl.sideEnd === 'left' || itemEl.sideEnd === 'right') {
            let sortVertSideEnd = itemEl.l2.calcAnchor[itemEl.sideEnd].sort(function(a, b) {
              return a.layerMeta.top - b.layerMeta.top;
            });
            indexSidePositionEnd = sortVertSideEnd.findIndex((element, index, array)=> {
              return element.layerMeta.top == currentTopEnd;
            });
          }
          else {
            let sortGorSideEnd = itemEl.l2.calcAnchor[itemEl.sideEnd].sort(function(a, b) {
              return a.layerMeta.left - b.layerMeta.left;
            });
            indexSidePositionEnd = sortGorSideEnd.findIndex((element, index, array)=> {
              return element.layerMeta.left == currentLeftEnd;
            });
          }
          itemEl.correctPosition.stop = calcValuePosition(itemEl.sideEnd, sideEndLength, indexSidePositionEnd);
        })
        
      }
      function calcValuePosition(side, lengthSide, indexSide) {
        switch(side) {
          case 'top':
            return { x: (size / (lengthSide + 1)) * (indexSide + 1), y: 0 };
            break;
          case 'right':
            return { x: size, y: (size / (lengthSide + 1)) * (indexSide + 1) };
            break;
          case 'bottom':
            return { x: (size / (lengthSide + 1)) * (indexSide + 1), y: size };
            break;
          case 'left':
            return { x: 0, y: (size / (lengthSide + 1)) * (indexSide + 1) };
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
        return `M${startX},${startY}C${pointStartX},${pointStartY} ${pointStopX},${pointStopY} ${stopX},${stopY}`
      }
      this.arrowsList = connectList;
    },
    findXPosition(event) {
      return (event.pageX - this.offset.offsetX) / this.networkScale
    },
    findYPosition(event) {
      return (event.pageY - this.offset.offsetY) / this.networkScale
    }
  }
}