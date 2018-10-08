<template lang="pug">
  .network-field(:id="'network' + netIndex")
    svg.svg-arrow(v-if="arrowsList.length")
      defs
        lineargradient(id="grad")
          stop(stop-color='black')
          stop(offset='100%' stop-color='magenta')
        marker#svg-arrow_triangle(
          refX="22" refY="3.25"
          markerWidth="8"
          markerHeight="8"
          orient="auto")
          polyline(points="0,0 0,6 6,3")
      template(
        v-for="(arrow, i) in arrowsList"
      )
        line.svg-arrow_line(marker-end="url(#svg-arrow_triangle)" :class="{'arrow--hidden': arrow.l1.meta.isInvisible || arrow.l2.meta.isInvisible}"
          :x1="arrow.l1.meta.left + 35"
          :y1="arrow.l1.meta.top + 35"
          :x2="arrow.l2.meta.left + 35"
          :y2="arrow.l2.meta.top + 35")
      //polygon(class="svg-arrow_triangle" :points="arrow.t1.x+','+arrow.t1.y+' '+arrow.t2.x+','+arrow.t2.y+' '+arrow.t3.x+','+arrow.t3.y")

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
    // test() {
    //   return this.workspace.network[0].meta.top
    // },
    workspace() {
      return this.$store.state.mod_workspace.workspaceContent[this.currentNetwork]
    },
    currentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
    // arrowsList() {
    //   let connectList = [];
    //   this.workspace.network.forEach((itemEl, indexEl, arrNet)=> {
    //
    //     if(itemEl.layerNext.length > 0) {
    //       itemEl.layerNext.forEach((itemCh, indexCh, arrCh)=> {
    //         let indexNextCh = findIndexId(arrNet, itemCh);
    //         let newArrow = {
    //           l1: {
    //             y: itemEl.meta.top + 35,
    //             x: itemEl.meta.left + 35
    //           },
    //           l2: {
    //             y: arrNet[indexNextCh].meta.top + 35,
    //             x: arrNet[indexNextCh].meta.left + 35
    //           }
    //         };
    //         connectList.push(newArrow);
    //       });
    //     }
    //   });
    //
    //   function findIndexId (arr, ID) {
    //     return arr.findIndex(function(item) {return item.layerId == ID});
    //   }
    //   //console.log(connectList)
    //   return connectList
    // }
  },
  watch: {
    workspace: {
      // handler: function (val, oldVal) {
      //
      // },
      // deep: true,
      // immediate: true
    }
  },
  methods: {
    createArrowList() {
      let listID = {};
      let connectList = [];
      let net = this.workspace;
      findAllID();

      net.network.forEach((itemEl, indexEl, arrNet)=> {
        if(itemEl.layerNext.length > 0) {
          itemEl.layerNext.forEach((itemCh, indexCh, arrCh)=> {
            //let indexNextCh = findIndexId(arrNet, itemCh);
            let newArrow = {
              l1: itemEl,
              l2: listID[itemCh]
            };
            connectList.push(newArrow);
          });
        }
      });
      console.log(connectList);

      // function findIndexId (arr, ID) {
      //   return arr.findIndex(function(item) {return item.layerId == ID});
      // }
      function findAllID() {
        net.network.forEach((itemEl, indexEl, arrNet)=> {
          let itemID = itemEl.layerId;
          listID[itemID] = itemEl;
        });
      }

      this.arrowsList = connectList;
    }
    // calcArrow(dot1, dot2) {
    //   let triangleSize = 8;
    //   let radians = Math.atan2((dot2.y - dot1.y), (dot2.x - dot1.x))
    //   let l1 = {x: dot1.x + 35, y: dot1.y + 35};
    //   let l2 = {x: dot2.x + 35, y: dot2.y + 35};
    //   //let lengthArrow = Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
    //   //console.log(lengthArrow)
    //
    //   let t1start = {x: l2.x - triangleSize, y: l2.y - triangleSize/2};
    //   let t2start = {x: l2.x - triangleSize, y: l2.y + triangleSize/2};
    //   let t3start = {x: l2.x, y: l2.y};
    //
    //   let t1 = turnСoordinate(t1start, l2, radians);
    //   let t2 = turnСoordinate(t2start, l2, radians);
    //   let t3 = turnСoordinate(t3start, l2, radians);
    //
    //   // let t1 = correctTriangle(t1x, radians);
    //   // let t2 = correctTriangle(t2x, radians);
    //   // let t3 = correctTriangle(t3x, radians);
    //
    //   //l1 = correctLine(l1, radians);
    //   //l2 = correctLine(l2, radians);
    //
    //   function turnСoordinate(dot, dotZero, rad) {
    //     let relX = dot.x - dotZero.x;
    //     let relY = dot.y - dotZero.y;
    //     let newX = (relX*Math.cos(rad) - relY*Math.sin(rad)) + dotZero.x;
    //     let newY = (relX*Math.sin(rad) + relY*Math.cos(rad)) + dotZero.y;
    //     let newDot = {
    //       x: roundNum(newX),
    //       y: roundNum(newY),
    //     };
    //     return newDot
    //   }
    //   function correctLine(finishDot, rad) {
    //     return {
    //       x: roundNum(finishDot.x - Math.cos(rad) * triangleSize/2),
    //       y: roundNum(finishDot.y - Math.sin(rad) * triangleSize/2),
    //     }
    //   }
    //   function correctTriangle(rt, rad) {
    //     return {
    //       x: roundNum(rt.x - Math.cos(rad) * triangleSize/3),
    //       y: roundNum(rt.y - Math.sin(rad) * triangleSize/3),
    //     }
    //   }
    //   function roundNum (num) {
    //     let accur = 100;
    //     return Math.round(num * accur) / accur;
    //   }
    //
    //   return {l1, l2, t1, t2, t3};
    //
    // },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  $color-arrow: #22DDE5;
  .svg-arrow {
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

