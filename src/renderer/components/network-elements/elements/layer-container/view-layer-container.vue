<template lang="pug">
  .btn.btn--layersbar.net-element-layercontainer(:draggable="draggable"
    data-component="LayerContainer"
    data-layer="Layer Container"
  )
    i.icon.icon-layer-net

</template>

<script>
export default {
  name: 'ViewLayerContainer',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
