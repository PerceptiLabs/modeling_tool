<template lang="pug">
  .btn.btn--layersbar.net-element-layercontainer(:draggable="draggable"
    data-component="LayerContainer"
    data-layer="Layer Container"
    data-type="Container"
    :style="layerStyles"
  )
    i.icon.icon-layer-net

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
  }
}
</script>
