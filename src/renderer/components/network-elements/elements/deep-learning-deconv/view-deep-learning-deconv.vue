<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningDeconv"
    data-layer="Deconvolution_1"
    data-type="Other"
    v-tooltip:right="'Deconvolution'"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-round-in

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDeepLearningDeconv',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Deep Learning Deconv',
        text: 'Deconvolutional layer'
      }
    }
  }
}
</script>
