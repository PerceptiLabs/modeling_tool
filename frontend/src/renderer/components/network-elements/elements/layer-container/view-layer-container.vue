<template lang="pug">
  .btn.btn--layersbar.net-element-layercontainer(:draggable="draggable"
    data-component="LayerContainer"
    data-layer="Layer Container"
    data-type="Container"
    :style="layerStyles"
  )
    i.icon.icon-layer-net
    i.icon.icon-layer-settings.openContainer

</template>

<script>
import mixinSet from '@/core/mixins/net-element-view-layer.js';

export default {
  name: 'ViewLayerContainer',
  mixins: [mixinSet],
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  },
}
</script>

<style scoped lang="scss">
  @import "../../../../scss/base";
  .icon.icon-layer-settings.openContainer {
    position: absolute;
    font-size: 1rem;
    right: 0.5rem;
    bottom: 0.5rem;
    color: $color-9;
    text-shadow: none;
  }
</style>