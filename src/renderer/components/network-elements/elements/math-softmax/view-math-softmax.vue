<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathSoftmax"
  data-layer="Softmax_1"
  data-type="Other"
  v-tooltip:right="'Softmax'"
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
