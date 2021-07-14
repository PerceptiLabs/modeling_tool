<template lang="pug">
  .network-field(
    :style="styleSvgArrow"
    :data-tutorial-target="statisticsIsOpen ? 'tutorial-statistics-map' : ''"
    ref="network"
    :class="{'isViewMode': isViewMode}"
    @mousedown="refNetworkMouseDown($event)"
  )
    network-grid(
      :gridStyle="gridStyle"
    )
    svg.svg-arrow(:style="styleSvgArrow" style="pointer-events: none")
      defs
        marker#svg-arrow_triangle(
            refX="3" refY="2"
            markerWidth="9"
            markerHeight="9"
            orient="auto"
          )
          polyline(points="0,0 0,4 3.5,2")
        marker#svg-arrow_triangle-empty(
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

      //- arrows list
      template(
        v-if="arrowsList.length"
        v-for="(arrow, index) in arrowsList"
      )
        //-'arrow--empty-output': arrow.l1.layerMeta.OutputDim.length === 0,
        path.svg-arrow_line(
          :class="arrowClassStyle(arrow)"
          :data-startid="arrow.l1.layerId"
          :data-stopid="arrow.l2.layerId"
          @click="focusArrow($event, arrow)"
          @blur="blurArrow"
          :d="arrow.positionArrow.path.arrow"
          :style="arrowStyle"
          style="pointer-events: all"
          tabindex="0"
          )
          //inline styles need for sreenshot

      //- pre arrow
      line.svg-arrow_line.arrow--hidden(
        v-if="preArrow.show"
        marker-end="url(#svg-arrow_triangle)"
        :stroke-dasharray="'none'"
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
      :with-layer-type-text="true"
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
    &.isViewMode {
      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 5;
      }
    }
  }
  .svg-arrow {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
    marker {
      fill: $arrow-color;
      stroke-width: 0;
    }
    marker#svg-arrow_triangle-empty {
      fill: $col-warning;
      stroke-width: 0;
    }
    marker#svg-arrow_triangle {
      fill: $arrow-color;
      stroke-width: 0;
    }
    marker.svg-arrow_marker_line--empty {
      fill: $col-warning;
      stroke-width: 0;
    }
    marker.svg-arrow_marker_multi-select {
      fill: $col-primary2;
      stroke-width: 0
    }
    marker#svg-arrow_end polyline {
      fill: #000
    }
  }
  .svg-arrow_line {
    stroke: $arrow-color; //inline styles for the canvas plagin
    stroke-width: 3;
    fill: transparent;
    &:hover {
      stroke-width: 4 !important;
      cursor: pointer;
    }
    &.is-focused {
      stroke-width: 5 !important;
    }
  }
  .svg-arrow_line--empty {
    stroke: $col-warning !important;
  }
  .svg-arrow_multi-select {
    fill: rgba($col-primary2, .15);
    stroke-width: 1;
    stroke: $col-primary2;
  }
</style>
