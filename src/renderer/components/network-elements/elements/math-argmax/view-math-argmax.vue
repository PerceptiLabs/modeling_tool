<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="false"  disabled="disabled"
  data-component="MathArgmax"
  data-layer="Argmax"
  data-type="Other"
  v-tooltip="'Argmax'"
  )
    i.icon.icon-l-calc-argmax

</template>

<script>
export default {
  name: 'ViewMathArgmax',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
