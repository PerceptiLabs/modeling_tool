<template lang="pug">
  .network-field(
    ref="network"
    @mousedown="refNetworkMouseDown($event)"
  )
    svg.svg-arrow(:style="styleSvgArrow")
      defs
        marker#svg-arrow_triangle(
          refX="3" refY="2.25"
          markerWidth="9"
          markerHeight="9"
          orient="auto"
          )
          polyline(points="0,0 0,4 3.5,2")
      //- arrows list
      template(
        v-if="arrowsList.length"
        v-for="arrow in arrowsList"
      )
        //-:stroke-dasharray="(arrow.type === 'solid' ? 'none' : (arrow.type === 'dash1' ? '7 6' : '14 7 3 7'))"
        path.svg-arrow_line(
          :class="{'arrow--empty-output': arrow.l1.layerMeta.OutputDim.length === 0, 'arrow--hidden': arrow.l1.layerMeta.isInvisible || arrow.l2.layerMeta.isInvisible}"
          :data-startid="arrow.l1.layerId"
          :data-stopid="arrow.l2.layerId"
          @focus="focusArrow($event)"
          marker-end="url(#svg-arrow_triangle)"
          stroke-dasharray="none"
          :d="arrow.positionArrow.path"
          style="stroke: #22DDE5; stroke-width: 3;fill: transparent;"
          )
      //- pre arrow
      line.svg-arrow_line.arrow--hidden(
        v-if="preArrow.show"
        marker-end="url(#svg-arrow_triangle)"
        :x1="preArrow.start.x"
        :y1="preArrow.start.y"
        :x2="preArrow.stop.x"
        :y2="preArrow.stop.y"
        )
      //-mouse multy select
      rect.svg-arrow_multi-select(
        v-if="multiSelect.show"
        :x="multiSelect.x"
        :y="multiSelect.y"
        :width="multiSelect.width"
        :height="multiSelect.height"
        rx="5"
        )
    component(
      v-for="el in networkElementList"
      :key="el.layerId"
      ref="layer"
      :is="el.componentName"
      :element-data="el"
    )

</template>

<script  src="./network-field.js"></script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .network-field {
    position: relative;
    flex: 1 1 100%;
    z-index: 1;
  }
  .svg-arrow {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    marker#svg-arrow_triangle {
      fill: $col-primary;
      stroke: $col-primary;
    }
  }
  .svg-arrow_line {
    stroke: $col-primary;
    stroke-width: 3;
    fill: transparent;
    &:focus {
      opacity: .5;
      stroke-width: 4;
    }
  }
  .svg-arrow_multi-select {
    fill: rgba($col-primary2, .15);
    stroke-width: 1;
    stroke: $col-primary2;
  }
</style>