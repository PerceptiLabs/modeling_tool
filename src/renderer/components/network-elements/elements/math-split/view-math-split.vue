<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathSplit"
  data-layer="Split"
  data-type="Other"
  v-tooltip:right="'Split'"
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
