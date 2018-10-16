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
  import IoInput from '@/components/network-elements/io-input.vue'
  import IoOutput from '@/components/network-elements/io-output.vue'
export default {
  name: 'NetworkField',
  components: {
    IoInput,
    IoOutput,
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
      return this.$store.state.mod_workspace.workspaceContent[this.netIndex]
    },
    // currentNetwork() {
    //   return this.$store.state.mod_workspace.currentNetwork
    // },

  },
  watch: {
    workspace() {
      this.createArrowList()
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

      console.log(connectList);



      function findAllID() {
        net.forEach((itemEl, indexEl, arrNet)=> {
         let itemID = itemEl.layerId;
         itemEl.calcAnchor = { top: 0, right: 0, bottom: 0, left: 0, /*tn: 1, rn: 1, bn: 1, ln: 1*/ };
         listID[itemID] = itemEl;
        });
      }
      function findPerspectiveSide() {
        net.forEach((itemEl, indexEl, arrNet)=> {
          if(itemEl.layerNext.length > 0) {
            itemEl.layerNext.forEach((itemCh, indexCh, arrCh)=> {
              let newArrow = {
                l1: itemEl,
                l2: listID[itemCh],
                correctPosition: {
                  x1: 0,
                  y1: 0,
                  x2: 0,
                  y2: 0
                }
              };
              Object.defineProperty(newArrow, 'positionArrow', {
                get() {
                  return {
                    x1: this.l1.meta.left + this.correctPosition.x1,
                    y1: this.l1.meta.top + this.correctPosition.y1,
                    x2: this.l2.meta.left + this.correctPosition.x2,
                    y2: this.l2.meta.top + this.correctPosition.y2,
                  }
                },
                enumerable: true,
                configurable: false
              });

              findSideMinLength(newArrow.l1, newArrow.l2);
              //console.log(newArrow, "<NEW ARROW");

              connectList.push(newArrow);
            });
          }
        });
      }
      function findSideMinLength(l1, l2) {
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

            ++l1.calcAnchor[TRsides.start.side];
            ++l2.calcAnchor[TRsides.end.side];
            break;

          case 'tl':
            let TLtop = topDot(l1);
            let TLleft = leftDot(l1);
            let TLbottom = bottomDot(l2);
            let TLright = rightDot(l2);
            let TLsides = calcMinLength(TLtop, TLleft, TLbottom, TLright);

            ++l1.calcAnchor[TLsides.start.side];
            ++l2.calcAnchor[TLsides.end.side];
            break;

          case 'br':
            let BRbottom = bottomDot(l1);
            let BRright = rightDot(l1);
            let BRtop = topDot(l2);
            let BRleft = leftDot(l2);
            let BRsides = calcMinLength(BRbottom, BRright, BRtop, BRleft);

            ++l1.calcAnchor[BRsides.start.side];
            ++l2.calcAnchor[BRsides.end.side];
            break;

          case 'bl':
            let BLbottom = bottomDot(l1);
            let BLleft = leftDot(l1);
            let BLtop = topDot(l2);
            let BLright = rightDot(l2);
            let BLsides = calcMinLength(BLbottom, BLleft, BLtop, BLright);

            ++l1.calcAnchor[BLsides.start.side];
            ++l2.calcAnchor[BLsides.end.side];
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
        //const minLen =
        return arrows.sort( (a, b) => a.length - b.length )[0];
      }
      function lengthLine(l1, l2) {
        return Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
      }
      function calcCorrectPosition() {
        connectList.forEach((itemArr, indexArr, listArr)=> {
          console.log(itemArr);
          calcDot(itemArr, itemArr.positionArrow);
        })
        function calcDot(el, out) {
          if(el.l1.calcAnchor.top > 0) {
            out.x1 = size / 2;
            out.y1 = 0
          }
          else if(el.l1.calcAnchor.right > 0) {
            out.x1 = size;
            out.y1 = size/2;
          }
          else if(el.l1.calcAnchor.bottom > 0) {
            out.x1 = size / 2;
            out.y1 = size
          }
          else if(el.l1.calcAnchor.left > 0) {
            out.x1 = 0;
            out.y1 = size / 2;
          }

          if(el.l2.calcAnchor.top > 0) {
            out.x2 = size / 2;
            out.y2 = 0
          }
          else if(el.l2.calcAnchor.right > 0) {
            out.x2 = size;
            out.y2 = size/2;
          }
          else if(el.l2.calcAnchor.bottom > 0) {
            out.x2 = size / 2;
            out.y2 = size
          }
          else if(el.l2.calcAnchor.left > 0) {
            out.x2 = 0;
            out.y2 = size / 2;
          }
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

