<template lang="pug">
  .btn.btn--layersbar.net-element-custom(:draggable="draggable"
  data-component="LayerCustom"
  data-layer="Layer Custom"
  data-type="Other"
  v-tooltip:bottom="'Custom'"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-custom

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewLayerCustom',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Custom',
        text: 'Custom layer'
      }
    }
  }
}
</script>
