<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainGan"
    data-layer="GAN"
    data-type="Training"
    v-tooltip:right="'GAN'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_training-gan"
    :style="layerStyles"
  )
    i.icon.icon-train-gan

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainGan',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train GAN',
        text: ''
      }
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../../scss/base";
  .icon {
    transform: translateX(3px);
  }
</style>
