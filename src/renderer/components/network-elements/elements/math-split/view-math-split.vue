<template lang="pug">
  button.btn.btn--layersbar.net-element-math(type="button" :draggable="draggable"
  data-component="MathSplit"
  data-layer="Split"
  )
    i.icon.icon-road-split

</template>

<script>
export default {
  name: 'ViewMathSplit',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
