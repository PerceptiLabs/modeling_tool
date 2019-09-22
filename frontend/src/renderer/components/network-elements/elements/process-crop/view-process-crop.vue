<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessCrop"
  data-layer="Crop"
  data-type="Other"
  v-tooltip:right="'Crop'"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-crop-symbol

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewProcessCrop',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Process Crop',
        text: 'Crop input data'
      }
    }
  }
}
</script>
