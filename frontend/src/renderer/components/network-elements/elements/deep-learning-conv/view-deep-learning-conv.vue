<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningConv"
    data-layer="Convolution"
    data-type="Other"
    v-tooltip:networkElement="'Convolution'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_convolution"
    :style="layerStyles"
  )
    i.icon.icon-round-out

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDeepLearningConv',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Deep Learning Conv',
        text: 'Convolutional layer'
      }
    }
  }
}
</script>
