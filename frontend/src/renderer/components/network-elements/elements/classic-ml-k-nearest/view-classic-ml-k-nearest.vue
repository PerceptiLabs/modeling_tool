<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLKNN"
    data-layer="K Nearest Neighbor"
    data-type="Training"
    v-tooltip:networkElement="'K Nearest Neighbor'"
    v-tooltip-interactive:right="interactiveInfo.MLKnn"
    :style="layerStyles"
  )
    i.icon.icon-round-figur

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewClassicMLKNN',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        MLKnn: {
          title: 'MLKnn',
          text: 'K Nearest neighbors layer'
        }
      }
    }
  }
}
</script>
