<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainReinforce"
    data-layer="Reinforcement Learning"
    data-type="Training"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-train-reinforce
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainReinforce',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train Reinforce',
        text: 'Reinforcement learning layer.'
      },
      displayTitle: 'Reinforce'
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
