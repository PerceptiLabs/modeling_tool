<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningConv"
    data-layer="Convolution"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_convolution"
    :style="layerStyles"
  )
    i.icon.icon-round-out
    .layerTitle(v-if="showTitle") {{ displayTitle }}

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
      },
      displayTitle: 'Convolution'
    }
  }
}
</script>
