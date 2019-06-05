<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessEmbed"
  data-layer="Word Embedding"
  data-type="Other"
  v-tooltip:right="'Word Embedding'"
  v-tooltip-interactive:right="interactiveInfo"
  )
    i.icon.icon-put-in-button

</template>

<script>
export default {
  name: 'ViewProcessEmbed',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  },
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
