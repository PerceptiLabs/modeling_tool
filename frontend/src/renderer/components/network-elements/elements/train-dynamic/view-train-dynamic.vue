<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainDynamic"
    data-layer="Dynamic Routing"
    data-type="Training"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-learning-dynamic
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainDynamic',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train Dynamic',
        text: 'Dynamic routing layer'
      },
      displayTitle: 'Dynamic'
    }
  }
}
</script>
