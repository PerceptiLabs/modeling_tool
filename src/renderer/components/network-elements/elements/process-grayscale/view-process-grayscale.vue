<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="false"  disabled="disabled"
  data-component="ProcessGrayscale"
  data-layer="Grayscale"
  data-type="Other"
  v-tooltip="'Grayscale'"
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
