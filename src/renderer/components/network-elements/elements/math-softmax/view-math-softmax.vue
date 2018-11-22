<template lang="pug">
  button.btn.btn--layersbar.net-element-math(type="button" :draggable="draggable"
  data-component="MathSoftmax"
  data-layer="Softmax"
  data-type="Other"
  v-tooltip="'Softmax'"
  )
    i.icon.icon-calc-softmax

</template>

<script>
export default {
  name: 'ViewMathSoftmax',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
