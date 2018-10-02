<template lang="pug">
  .network-field(:id="'network' + netIndex")
    svg.svg-arrow(
      v-if="arrowsList.length"
      v-for="(arrow, i) in arrowsList"
      :key="arrow.i"
      )
      line(class="svg-arrow_line" :x1="arrow.l1.x" :y1="arrow.l1.y" :x2="arrow.l2.x" :y2="arrow.l2.y")
      polygon(class="svg-arrow_triangle" :points="arrow.t1.x+','+arrow.t1.y+' '+arrow.t2.x+','+arrow.t2.y+' '+arrow.t3.x+','+arrow.t3.y")

    component(
      v-for="(el, index) in workspace.network"
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
      //arrowsList: []
    }
  },
  mounted() {
    //this.calcArrow({x:200,y:200},{x:300,y:400})
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
    arrowsList() {
      let connectList = [];
      this.workspace.network.forEach((itemEl, indexEl, arrNet)=> {

        if(itemEl.layerNext.length > 0) {
          itemEl.layerNext.forEach((itemCh, indexCh, arrCh)=> {
            let indexNextCh = findIndexId(arrNet, itemCh);
            let newArrow = {
              l1: {
                y: itemEl.meta.top,
                x: itemEl.meta.left
              },
              l2: {
                y: arrNet[indexNextCh].meta.top,
                x: arrNet[indexNextCh].meta.left
              }
            }
            connectList.push(this.calcArrow(newArrow.l1, newArrow.l2))
          });
        }
      });

      function findIndexId (arr, ID) {
        return arr.findIndex(function(item) {return item.layerId == ID});
      }

      //console.log(connectList)

      return connectList
    }
  },
  methods: {
    calcArrow(dot1, dot2) {
      let triangleSize = 8;
      let radians = Math.atan2((dot2.y - dot1.y), (dot2.x - dot1.x))
      let l1 = {x: dot1.x, y: dot1.y + 35};
      let l2 = {x: dot2.x, y: dot2.y + 35};
      //let lengthArrow = Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
      //console.log(lengthArrow)

      let t1start = {x: l2.x - triangleSize, y: l2.y - triangleSize/2};
      let t2start = {x: l2.x - triangleSize, y: l2.y + triangleSize/2};
      let t3start = {x: l2.x, y: l2.y};

      let t1 = turnСoordinate(t1start, l2, radians);
      let t2 = turnСoordinate(t2start, l2, radians);
      let t3 = turnСoordinate(t3start, l2, radians);

      // let t1 = correctTriangle(t1x, radians);
      // let t2 = correctTriangle(t2x, radians);
      // let t3 = correctTriangle(t3x, radians);

      //l1 = correctLine(l1, radians);
      l2 = correctLine(l2, radians);

      function turnСoordinate(dot, dotZero, rad) {
        let relX = dot.x - dotZero.x;
        let relY = dot.y - dotZero.y;
        let newX = (relX*Math.cos(rad) - relY*Math.sin(rad)) + dotZero.x;
        let newY = (relX*Math.sin(rad) + relY*Math.cos(rad)) + dotZero.y;
        let newDot = {
          x: roundNum(newX),
          y: roundNum(newY),
        };
        return newDot
      }
      function correctLine(finishDot, rad) {
        return {
          x: roundNum(finishDot.x - Math.cos(rad) * triangleSize/2),
          y: roundNum(finishDot.y - Math.sin(rad) * triangleSize/2),
        }
      }
      // function correctTriangle(rt, rad) {
      //   return {
      //     x: roundNum(rt.x - Math.cos(rad) * triangleSize/3),
      //     y: roundNum(rt.y - Math.sin(rad) * triangleSize/3),
      //   }
      // }
      function roundNum (num) {
        let accur = 100;
        return Math.round(num * accur) / accur;
      }

      return {l1, l2, t1, t2, t3};
    }
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
  }
  .svg-arrow_line {
    stroke: $color-arrow;
    stroke-width: 3;
  }
  .svg-arrow_triangle {
    fill: $color-arrow;
    stroke: $color-arrow;
  }
</style>

