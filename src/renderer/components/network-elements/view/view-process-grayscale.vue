<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessGrayscale"
  data-layer="Grayscale"
  )
    i.icon.icon-sieve

</template>

<script>
export default {
  name: 'ViewProcessGrayscale',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
