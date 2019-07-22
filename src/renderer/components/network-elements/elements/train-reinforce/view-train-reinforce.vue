<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainReinforce"
    data-layer="Reinforcement Learning"
    data-type="Training"
    v-tooltip:right="'Reinforcement Learning'"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-learning-reinforcement1

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
      }
    }
  }
}
</script>
