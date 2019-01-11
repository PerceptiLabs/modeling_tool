<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="false"  disabled="disabled"
  data-component="MathSoftmax"
  data-layer="Softmax"
  data-type="Other"
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
