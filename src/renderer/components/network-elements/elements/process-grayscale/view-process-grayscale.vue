<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessGrayscale"
    data-layer="Grayscale_1"
    data-type="Other"
    v-tooltip:right="'Grayscale'"
    v-tooltip-interactive:right="interactiveInfo"
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
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Process Grayscale',
        text: 'Convert data to grayscale'
      }
    }
  }
}
</script>
