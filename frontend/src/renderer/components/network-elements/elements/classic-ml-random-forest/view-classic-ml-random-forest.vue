<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLRandomForest"
    data-layer="Random Forest"
    data-type="Training"
    v-tooltip:right="'Random Forest'"
    v-tooltip-interactive:right="interactiveInfo.MLRandomForest"
    :style="layerStyles"
  )
    i.icon.icon-trees

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewClassicMLRandomForest',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        MLRandomForest: {
          title: 'ML Random Forest',
          text: 'Random forest layer'
        }
      }
    }
  }
}
</script>
