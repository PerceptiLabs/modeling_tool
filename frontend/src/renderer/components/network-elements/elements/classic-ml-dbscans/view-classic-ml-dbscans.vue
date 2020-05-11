<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLDbscans"
    data-layer="DBSCAN"
    data-type="Training"
    v-tooltip:bottom="'DBSCAN'"
    v-tooltip-interactive:right="interactiveInfo.MLDbscan"
    :style="layerStyles"
  )
    i.icon.icon-round-three

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewClassicMLDbscans',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        MLDbscan: {
          title: 'MLDbscan',
          text: 'Choose which method to use'
        }
      }
    }
  }
}
</script>
