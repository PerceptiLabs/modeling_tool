<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLSVM"
    data-layer="Support Vector Machine"
    data-type="Training"
    v-tooltip:bottom="'Support Vector Machine'"
    v-tooltip-interactive:right="interactiveInfo.MLSvm"
    :style="layerStyles"
  )
    i.icon.icon-round-figur2

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewClassicMLSVM',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        MLSvm: {
          title: 'MLSvm',
          text: 'SVM layer'
        }
      }
    }
  }
}
</script>
