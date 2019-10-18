<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainOptimizer"
    data-layer="Optimizer"
    data-type="Training"
    v-tooltip:right="'Optimizer'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_training-normal"
    :style="layerStyles"
  )
    i.icon.icon-train-optimaze

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainOptimizer',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train Optimizer',
        text: 'Normal supervised learning layer'
      }
    }
  }
}
</script>
