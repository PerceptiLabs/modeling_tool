<template lang="pug">
  button.btn.btn--layersbar.net-element-math(type="button" :draggable="draggable"
  data-component="MathArgmax"
  data-layer="Argmax"
  data-type="Other"
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
