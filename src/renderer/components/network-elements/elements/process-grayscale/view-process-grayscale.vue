<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessGrayscale"
  data-layer="Grayscale_1"
  data-type="Other"
  v-tooltip:right="'Grayscale'"

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
