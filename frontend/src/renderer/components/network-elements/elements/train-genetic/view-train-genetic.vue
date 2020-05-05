<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
  data-component="TrainGenetic"
  data-layer="Genetic Algorithm"
  data-type="Training"
  v-tooltip:bottom="'Genetic Algorithm'"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-learning-genetic

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewTrainGenetic',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Train GA',
        text: 'Genetic algorithm layer'
      }
    }
  }
}
</script>
