<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainRegression"
    data-layer="Regression"
    data-type="Training"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_training-regression"
    :style="layerStyles"
  )
    i.icon.icon-train-regression
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainRegression',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train Regression',
        text: 'Regression supervised learning layer'
      },
      displayTitle: 'Regression'
    }
  }
}
</script>
