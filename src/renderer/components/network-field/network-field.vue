<template lang="pug">
  .network-field(:id="'network' + netIndex")
    svg.svg-arrow(v-if="arrowsList.length")
      defs
        lineargradient(id="grad")
          stop(stop-color='black')
          stop(offset='100%' stop-color='magenta')
        marker#svg-arrow_triangle(
          refX="3" refY="2.25"
          markerWidth="9"
          markerHeight="9"
          orient="auto")
          polyline(points="0,0 0,4 3.5,2")
      template(
        v-for="(arrow, i) in arrowsList"
      )
        line.svg-arrow_line(
          marker-end="url(#svg-arrow_triangle)"
          :class="{'arrow--hidden': arrow.l1.meta.isInvisible || arrow.l2.meta.isInvisible}"
          :stroke-dasharray="(arrow.type === 'solid' ? 'none' : (arrow.type === 'dash1' ? '7 6' : '14 7 3 7'))"
          :x1="arrow.positionArrow.x1"
          :y1="arrow.positionArrow.y1"
          :x2="arrow.positionArrow.x2"
          :y2="arrow.positionArrow.y2")

    component(
      v-for="(el, index) in workspace.network"
      :class="{'element--hidden': el.meta.isInvisible}"
      :key="el.index"
      :is="el.componentName"
      :elementData="{el, index}"
    )

</template>

<script>
  
  import IoInput              from '@/components/network-elements/elements/io-input.vue'
  import IoOutputBackprop     from '@/components/network-elements/elements/io-output-backpropagation.vue'
  import IoOutputGenetic      from '@/components/network-elements/elements/io-output-genetic-algorithm.vue'
  import IoOutputRouting      from '@/components/network-elements/elements/io-output-routing-algorithm.vue'

  import DataData             from '@/components/network-elements/elements/data-data.vue'
  import DataEnvironment      from '@/components/network-elements/elements/data-environment.vue'

  import LearnDeepConnect     from '@/components/network-elements/elements/learn-deep-connect.vue'
  import LearnDeepConvolut    from '@/components/network-elements/elements/learn-deep-convolut.vue'
  import LearnDeepDeconvolut  from '@/components/network-elements/elements/learn-deep-deconvolut.vue'
  import LearnDeepRecurrent   from '@/components/network-elements/elements/learn-deep-recurrent.vue'

  import ProcessCrop          from '@/components/network-elements/elements/process-crop.vue'
  import ProcessEmbed         from '@/components/network-elements/elements/process-embed.vue'
  import ProcessGrayscale     from '@/components/network-elements/elements/process-grayscale.vue'
  import ProcessHot           from '@/components/network-elements/elements/process-hot.vue'
  import ProcessReshape       from '@/components/network-elements/elements/process-reshape.vue'

  import TrainNormal          from '@/components/network-elements/elements/train-normal.vue'
  import TrainNormalData      from '@/components/network-elements/elements/train-normal-data.vue'
  import TrainGenetic         from '@/components/network-elements/elements/train-genetic.vue'
  import TrainDynamic         from '@/components/network-elements/elements/train-dynamic.vue'
  import TrainReinforce       from '@/components/network-elements/elements/train-reinforce.vue'

  import MathArgmax           from '@/components/network-elements/elements/math-argmax.vue'
  import MathMerge            from '@/components/network-elements/elements/math-merge.vue'
  import MathSoftmax          from '@/components/network-elements/elements/math-softmax.vue'
  import MathSplit            from '@/components/network-elements/elements/math-split.vue'

  import LearnClassDbscans    from '@/components/network-elements/elements/learn-class-dbscans.vue'
  import LearnClassKMeans     from '@/components/network-elements/elements/learn-class-k-means.vue'
  import LearnClassKNearest   from '@/components/network-elements/elements/learn-class-k-nearest.vue'
  import LearnClassRandomForest  from '@/components/network-elements/elements/learn-class-random-forest.vue'
  import LearnClassVectorMachine from '@/components/network-elements/elements/learn-class-vector-machine.vue'

  import LayerContainer       from '@/components/network-elements/elements/layer-container.vue'

export default {
  name: 'NetworkField',
  components: {
    IoInput,
    IoOutputBackprop,
    IoOutputGenetic,
    IoOutputRouting,
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
    TrainNormalData,
    TrainGenetic,
    TrainDynamic,
    TrainReinforce,
    MathArgmax,
    MathMerge,
    MathSoftmax,
    MathSplit,
    LearnClassDbscans,
    LearnClassKMeans,
    LearnClassKNearest,
    LearnClassRandomForest,
    LearnClassVectorMachine,
    LayerContainer
  },
  props: ['netIndex'],
  data() {
    return {
      arrowsList: []
    }
  },
  mounted() {
    this.createArrowList()
  },
  computed: {
    workspace() {
      return this.$store.state.mod_workspace.workspaceContent[this.currentNetwork]
    },
    startId() {
      return this.$store.state.mod_workspace.startArrowID
    },
    currentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },

  },
  watch: {
    workspace() {
      this.createArrowList()
    },
    startId(newId) {
      if(newId == null) {
        this.createArrowList()
      }
    }
  },
  methods: {
    createArrowList() {
      const size = 72;
      const listID = {};
      const connectList = [];
      const net = this.workspace.network;
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
          if(itemEl.connectionOut.length > 0) {
            for (var numEl in itemEl.connectionOut) {
              let outEl = itemEl.connectionOut[numEl];
              let newArrow = {
                l1: itemEl,
                l2: listID[outEl.id],
                type: outEl.type,
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
                  return {
                    x1: this.l1.meta.left + this.correctPosition.start.x,
                    y1: this.l1.meta.top + this.correctPosition.start.y,
                    x2: this.l2.meta.left + this.correctPosition.stop.x,
                    y2: this.l2.meta.top + this.correctPosition.stop.y,
                  }
                },
                enumerable: true,
                configurable: false
              });
              findSideMinLength(newArrow.l1, newArrow.l2, newArrow);
              connectList.push(newArrow);
            }
          }
        });
      }
      function findSideMinLength(l1, l2, currentEl) {
        let position = '';
        (l1.meta.top <= l2.meta.top) ? position = position + 'b' : position = position + 't';
        (l1.meta.left <= l2.meta.left) ? position = position + 'r' : position = position + 'l';

        // const offsetX = Math.abs(l1.meta.left - l2.meta.left);
        // const offsetY = Math.abs(l1.meta.top - l2.meta.top);

        function topDot(dot) {
          return {
            side: 'top',
            x: dot.meta.left + (size / 2),
            y: dot.meta.top
          }
        }
        function rightDot(dot) {
          return {
            side: 'right',
            x: dot.meta.left + size,
            y: dot.meta.top + (size / 2)
          }
        }
        function bottomDot(dot) {
          return {
            side: 'bottom',
            x: dot.meta.left + (size / 2),
            y: dot.meta.top + size
          }
        }
        function leftDot(dot) {
          return {
            side: 'left',
            x: dot.meta.left,
            y: dot.meta.top + (size / 2)
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
          {
            length: lengthLine(d1, d3),
            start: d1,
            end: d3,
          },
          {
            length: lengthLine(d1, d4),
            start: d1,
            end: d4,
          },
          {
            length: lengthLine(d2, d3),
            start: d2,
            end: d3,
          },
          {
            length: lengthLine(d2, d4),
            start: d2,
            end: d4,
          }
        ];
        return arrows.sort( (a, b) => a.length - b.length )[0];
      }
      function lengthLine(l1, l2) {
        return Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
      }
      function calcCorrectPosition() {
        connectList.forEach((itemEl, itemIndex, itemArr)=> {
          let currentLeftStart = itemEl.l2.meta.left;
          let currentTopStart = itemEl.l2.meta.top;
          let currentLeftEnd = itemEl.l1.meta.left;
          let currentTopEnd = itemEl.l1.meta.top;
          let indexSidePositionStart = '';
          let indexSidePositionEnd = '';
          let sideStartLength = itemEl.l1.calcAnchor[itemEl.sideStart].length;
          let sideEndLength = itemEl.l2.calcAnchor[itemEl.sideEnd].length;

          //calc start
          if(itemEl.sideStart === 'left' || itemEl.sideStart === 'right') {
            let sortVertSideStart = itemEl.l1.calcAnchor[itemEl.sideStart].sort(function(a, b) {
              return a.meta.top - b.meta.top;
            });
            indexSidePositionStart = sortVertSideStart.findIndex((element, index, array)=> {
              return element.meta.top == currentTopStart;
            });
          }
          else {
            let sortGorSideStart = itemEl.l1.calcAnchor[itemEl.sideStart].sort(function(a, b) {
              return a.meta.left - b.meta.left;
            });
            indexSidePositionStart = sortGorSideStart.findIndex((element, index, array)=> {
              return element.meta.left == currentLeftStart;
            });
          }
          itemEl.correctPosition.start = calcValuePosition(itemEl.sideStart, sideStartLength, indexSidePositionStart);
          //calc END
          if(itemEl.sideEnd === 'left' || itemEl.sideEnd === 'right') {
            let sortVertSideEnd = itemEl.l2.calcAnchor[itemEl.sideEnd].sort(function(a, b) {
              return a.meta.top - b.meta.top;
            });
            indexSidePositionEnd = sortVertSideEnd.findIndex((element, index, array)=> {
              return element.meta.top == currentTopEnd;
            });
          }
          else {
            let sortGorSideEnd = itemEl.l2.calcAnchor[itemEl.sideEnd].sort(function(a, b) {
              return a.meta.left - b.meta.left;
            });
            indexSidePositionEnd = sortGorSideEnd.findIndex((element, index, array)=> {
              return element.meta.left == currentLeftEnd;
            });
          }
          itemEl.correctPosition.stop = calcValuePosition(itemEl.sideEnd, sideEndLength, indexSidePositionEnd);
        })
      }
      function calcValuePosition(side, lengthSide, indexSide) {
        switch(side) {
          case 'top':
            return {
              x: (size / (lengthSide + 1)) * (indexSide + 1),
              y: 0
            };
            break;
          case 'right':
            return {
              x: size,
              y: (size / (lengthSide + 1)) * (indexSide + 1),
            };
            break;
          case 'bottom':
            return {
              x: (size / (lengthSide + 1)) * (indexSide + 1),
              y: size
            };
            break;
          case 'left':
            return {
              x: 0,
              y: (size / (lengthSide + 1)) * (indexSide + 1),
            };
            break;
        }
      }

      this.arrowsList = connectList;
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  $color-arrow: #22DDE5;
  .svg-arrow {
    pointer-events: none;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    marker#svg-arrow_triangle {
      fill: $color-arrow;
      stroke: $color-arrow;
    }
  }
  .svg-arrow_line {
    stroke: $color-arrow;
    stroke-width: 3;
  }


</style>

