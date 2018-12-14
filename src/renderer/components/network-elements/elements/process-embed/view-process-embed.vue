<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="false"  disabled="disabled"
  data-component="ProcessEmbed"
  data-layer="Word Embedding"
  data-type="Other"
  v-tooltip="'Word Embedding'"
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
