<template lang="pug">
  .layer-colorpicker
    .layer-item-color-block(type="button"
      :class="layerItemColor"
      )
</template>

<script>
import { layerBgColor }       from '@/core/helpers.js'
  
export default {
  name: 'SidebarLayersColorPicker',
  props: {
    currentLayer: {
      type: Object,
      default: function () {
        return null
      }
    },
  },
  computed: {
    layerItemColor() {
      return layerBgColor(this.currentLayer.componentName)
    },
  },

}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .layer-item-color-block {
    width: 8px;
    height: 8px;
    border-radius: 2px;
  }
</style>
