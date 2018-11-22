<template lang="pug">
  button.btn.btn--layersbar.net-element-math(type="button" :draggable="draggable"
  data-component="MathMerge"
  data-layer="Merge"
  data-type="Other"
  v-tooltip="'Merge'"
  )
    i.icon.icon-road-concat

</template>

<script>
export default {
  name: 'ViewMathMerge',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
