<template lang="pug">
  .network-field(
    ref="network"
    @mousedown="refNetworkMouseDown($event)"
  )
    svg.svg-arrow(:style="styleSvgArrow")
      defs
        marker#svg-arrow_triangle.svg-arrow_marker(
          refX="3" refY="2"
          markerWidth="9"
          markerHeight="9"
          orient="auto"
          )
          polyline(points="0,0 0,4 3.5,2")

        //-marker#svg-arrow_start.svg-arrow_marker(
          viewBox="0 0 28 16"
          refX="0" refY="7"
          markerWidth="8"
          markerHeight="14"
          orient="auto"
          markerUnits="strokeWidth"
          )
          ellipse(ry="7" rx="8" cy="7" cx="0")

        //-marker#svg-arrow_end.svg-arrow_marker(
          viewBox="0 0 28 16"
          refX="8" refY="7"
          markerWidth="8"
          markerHeight="14"
          orient="auto"
          markerUnits="strokeWidth"
          )
          ellipse(ry="7" rx="8" cy="7" cx="8")
          polyline(points="1.9566014856100082,3.9975550174713135 1.9566014856100082,10.002445220947266 7.119192227721214,7")
      //- arrows list
      template(
        v-if="arrowsList.length"
        v-for="arrow in arrowsList"
      )
        //-'arrow--empty-output': arrow.l1.layerMeta.OutputDim.length === 0,
        path.svg-arrow_line(
          :class="{'arrow--hidden': arrow.l1.layerMeta.isInvisible || arrow.l2.layerMeta.isInvisible}"
          :data-startid="arrow.l1.layerId"
          :data-stopid="arrow.l2.layerId"
          @focus="focusArrow($event)"
          marker-end="url(#svg-arrow_triangle)"
          :d="arrow.positionArrow.path.arrow"
          style="stroke: #22DDE5; strokeWidth: 3; fill: transparent"
          )
          //inline styles need for sreenshot

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
    //-settings-arrow(
      v-if="arrowsList.length"
      v-for="(arrow, i) in arrowsList"
      /:key="arrow.i"
      /:arrow-data="arrow"
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
  .network-field--show-code {
    transform: translate(0);
  }
  .svg-arrow {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
    marker.svg-arrow_marker {
      fill: $col-primary;
      stroke-width: 0
    }
    marker#svg-arrow_end polyline {
      fill: #000
    }
  }
  .svg-arrow_line {
    stroke: $col-primary;
    stroke-width: 3;
    fill: transparent;
    &:focus {
      stroke-width: 5;
    }
  }
  .svg-arrow_multi-select {
    fill: rgba($col-primary2, .15);
    stroke-width: 1;
    stroke: $col-primary2;
  }
  .test {
    position: absolute;
    height: 20px;
    width: 20px;
    background-color: #fff;
  }
</style>