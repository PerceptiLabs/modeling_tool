<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainDetector"
    data-layer="Detector"
    data-type="Training"
    v-tooltip:right="'Detector'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_training-detector"
    :style="layerStyles"
  )
    i.icon.icon-training

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainDetector',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train Detector',
        text: 'Detector supervised learning layer'
      }
    }
  }
}
</script>
