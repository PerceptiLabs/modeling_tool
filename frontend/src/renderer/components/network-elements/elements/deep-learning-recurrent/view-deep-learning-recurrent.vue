<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningRecurrent"
    data-layer="Recurrent"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-round-left
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDeepLearningRecurrent',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Deep Learning Recurrent',
        text: 'Recurrent layer'
      },
      displayTitle: 'Recurrent'
    }
  }
}
</script>
