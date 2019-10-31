<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainLoss"
    data-layer="Loss"
    data-type="Training"
    v-tooltip:right="'Loss'"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-train-loss

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainLoss',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train Loss',
        text: 'Normal supervised learning layer'
      }
    }
  }
}
</script>
