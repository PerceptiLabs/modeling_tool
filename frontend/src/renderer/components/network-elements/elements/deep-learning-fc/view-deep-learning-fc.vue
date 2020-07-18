<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
  data-component="DeepLearningFC"
  data-layer="Fully Connected"
  data-type="Other"
  v-tooltip-interactive:right="interactiveInfo"
  id="tutorial_fully-connected"
    :style="layerStyles"
  )
    i.icon.icon-round
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDeepLearningFC',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Deep Learning FC',
        text: 'Fully Connected layer'
      },
      displayTitle: 'Fully connected'
    }
  }
}
</script>
