<template lang="pug">
  .btn.btn--layersbar.net-element-custom(:draggable="draggable"
  data-component="LayerCustom"
  data-layer="Layer Custom"
  data-type="Other"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-custom
    .layerTitle(v-if="showTitle") {{ displayTitle }}

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
      },
      displayTitle: 'Custom'
    }
  }
}
</script>
