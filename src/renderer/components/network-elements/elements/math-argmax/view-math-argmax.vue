<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathArgmax"
  data-layer="Argmax_1"
  data-type="Other"
  v-tooltip:right="'Argmax'"
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
