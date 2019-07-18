<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessEmbed"
  data-layer="Word Embedding"
  data-type="Other"
  v-tooltip:right="'Word Embedding'"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-put-in-button

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewProcessEmbed',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Process WordEmbedding',
        text: 'Use word embedding'
      }
    }
  }
}
</script>
