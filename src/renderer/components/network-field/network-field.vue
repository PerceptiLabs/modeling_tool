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
      let size = 72;
      let listID = {};
      let connectList = [];
      let net = this.workspace.network;
      findAllID();

      net.forEach((itemEl, indexEl, arrNet)=> {
        if(itemEl.layerNext.length > 0) {
          itemEl.layerNext.forEach((itemCh, indexCh, arrCh)=> {
            //let indexNextCh = findIndexId(arrNet, itemCh);
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

            calcSideArrow(newArrow, itemEl, listID[itemCh]);
            //console.log(newArrow, "<NEW ARROW");
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
            connectList.push(newArrow);
          });
        }
      });

      calcCorrectPosition(connectList);
      //console.log(connectList);

      function calcCorrectPosition(arrList) {
        arrList.forEach((itemArr, indexArr, listArr)=> {
          if(itemArr.l1.calcAnchor.bottom && itemArr.l2.calcAnchor.top) {
            itemArr.correctPosition.x1 = size - itemArr.l1.calcAnchor.bn * (size/(itemArr.l1.calcAnchor.bottom + 1));
            itemArr.correctPosition.x2 = size - itemArr.l2.calcAnchor.tn * (size/(itemArr.l2.calcAnchor.top + 1));
            itemArr.correctPosition.y1 = size;
            itemArr.correctPosition.y2 = 0;

            itemArr.l1.calcAnchor.bn = ++itemArr.l1.calcAnchor.bn;
            itemArr.l2.calcAnchor.tn = ++itemArr.l2.calcAnchor.tn;
          }
          if(itemArr.l1.calcAnchor.top && itemArr.l2.calcAnchor.bottom) {
            itemArr.correctPosition.x1 = size - itemArr.l1.calcAnchor.tn * (size/(itemArr.l1.calcAnchor.top + 1));
            itemArr.correctPosition.x2 = size - itemArr.l2.calcAnchor.bn * (size/(itemArr.l2.calcAnchor.bottom + 1));
            itemArr.correctPosition.y1 = 0;
            itemArr.correctPosition.y2 = size;

            itemArr.l1.calcAnchor.tn = ++itemArr.l1.calcAnchor.tn;
            itemArr.l2.calcAnchor.bn = ++itemArr.l2.calcAnchor.bn;
          }
          if(itemArr.l1.calcAnchor.right && itemArr.l2.calcAnchor.left) {
            itemArr.correctPosition.x1 = size;
            itemArr.correctPosition.x2 = 0;
            itemArr.correctPosition.y1 = size - itemArr.l1.calcAnchor.rn * (size/(itemArr.l1.calcAnchor.right + 1));
            itemArr.correctPosition.y2 = size - itemArr.l2.calcAnchor.ln * (size/(itemArr.l2.calcAnchor.left + 1));

            itemArr.l1.calcAnchor.rn = ++itemArr.l1.calcAnchor.rn;
            itemArr.l2.calcAnchor.ln = ++itemArr.l2.calcAnchor.ln;
          }
          if(itemArr.l1.calcAnchor.left && itemArr.l2.calcAnchor.right) {
            itemArr.correctPosition.x1 = 0;
            itemArr.correctPosition.x2 = size;
            itemArr.correctPosition.y1 = size - itemArr.l1.calcAnchor.ln * (size/(itemArr.l1.calcAnchor.left + 1));
            itemArr.correctPosition.y2 = size - itemArr.l2.calcAnchor.rn * (size/(itemArr.l2.calcAnchor.right + 1));

            itemArr.l1.calcAnchor.ln = ++itemArr.l1.calcAnchor.ln;
            itemArr.l2.calcAnchor.rn = ++itemArr.l2.calcAnchor.rn;
          }
        });
      }

      function calcSideArrow(arrow, startEl, stopEl) {

        const sideL1Right = arrow.l1.meta.left < arrow.l2.meta.left;
        const sideL1Bottom = arrow.l1.meta.top < arrow.l2.meta.top;

        const offsetX = Math.abs(arrow.l1.meta.left - arrow.l2.meta.left);
        const offsetY = Math.abs(arrow.l1.meta.top - arrow.l2.meta.top);

        if(sideL1Right && offsetX > offsetY) {
          startEl.calcAnchor.right = ++startEl.calcAnchor.right;
          stopEl.calcAnchor.left = ++stopEl.calcAnchor.left
        }
        if(!sideL1Right && offsetX > offsetY) {
          startEl.calcAnchor.left = ++startEl.calcAnchor.left;
          stopEl.calcAnchor.right = ++stopEl.calcAnchor.right;
        }
        if(sideL1Bottom && offsetX < offsetY) {
          startEl.calcAnchor.bottom = ++startEl.calcAnchor.bottom;
          stopEl.calcAnchor.top = ++stopEl.calcAnchor.top
        }
        if(!sideL1Bottom && offsetX < offsetY) {
          startEl.calcAnchor.top = ++startEl.calcAnchor.top;
          stopEl.calcAnchor.bottom = ++stopEl.calcAnchor.bottom
        }
      }

      function findAllID() {
        net.forEach((itemEl, indexEl, arrNet)=> {
          let itemID = itemEl.layerId;
          itemEl.calcAnchor = { top: 0, right: 0, bottom: 0, left: 0, tn: 1, rn: 1, bn: 1, ln: 1 };
          listID[itemID] = itemEl;
        });
      }
      function lengthLine(l1, l2) {
        return Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
      }
      function findMinLength(l1, l2) {

        let position = '';

        (l1.meta.top < l2.meta.top) ? position = position + 't' : position = position + 'b';
        (l1.meta.left < l2.meta.left) ? position = position + 'r' : position = position + 'l';


        const offsetX = Math.abs(arrow.l1.meta.left - arrow.l2.meta.left);
        const offsetY = Math.abs(arrow.l1.meta.top - arrow.l2.meta.top);

        function topDot(dot) {
          return {
            x: dot.x + (size / 2),
            y: dot.y
          }
        }
        function rightDot(dot) {
          return {
            x: dot.x + size,
            y: dot.y + (size / 2)
          }
        }
        function bottomDot(dot) {
          return {
            x: dot.x + (size / 2),
            y: dot.y + size
          }
        }
        function leftDot(dot) {
          return {
            x: dot.x,
            y: dot.y + (size / 2)
          }
        }

        switch(position) {
          case 'tr':
            let top = topDot(l1);
            let right = rightDot(l1);
            let bottom = bottomDot(l2);
            let left = leftDot(l2);
            calcMinLength(top, right, bottom, left);


          //   break
          // case 'tl':
          //   break
          // case 'br':
          //   break
          // case 'bl':
          //   break
        }
      }

      function calcMinLength(d1, d2, d3, d4) {
        let d1d3 = lengthLine(d1, d3);
        let d1d4 = lengthLine(d1, d4);
        let d2d3 = lengthLine(d2, d3);
        let d2d4 = lengthLine(d2, d4);

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
        ]

        // let lineArr = [d1d3, d1d4, d2d3, d2d4].sort();
        // let minLine = lineArr[0];
        const minLen = arrows.sort( (a, b) => a.length - b.length )[0];
        return minLen;
      }
      //console.log(listID);
      this.arrowsList = connectList;
      //this.calcArrowsPosition()
    },

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

