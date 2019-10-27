<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLKMeans"
    data-layer="K-Means Clustering"
    data-type="Training"
    v-tooltip:right="'K-Means Clustering'"
    v-tooltip-interactive:right="interactiveInfo.MLKmeans"
    :style="layerStyles"
  )
    i.icon.icon-round-sieve

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewClassicMLKMeans',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        MLKmeans: {
          title: 'MLKmeans',
          text: 'K means clustering layer.'
        }
      }
    }
  }
}
</script>
