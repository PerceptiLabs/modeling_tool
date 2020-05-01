<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainNormal"
    data-layer="Normal"
    data-type="Training"
    v-tooltip:right="'Image Classification'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_training-normal"
    :style="layerStyles"
  )
    i.icon.icon-training

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainNormal',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Image Classification',
        text: 'Normal supervised learning layer'
      }
    }
  }
}
</script>
