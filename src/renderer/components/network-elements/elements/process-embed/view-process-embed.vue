<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessEmbed"
  data-layer="Word Embedding"
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
  }
}
</script>
