<template lang="pug">
  button.btn.btn--layersbar.net-element-math(type="button" :draggable="draggable"
  data-component="MathMerge"
  data-layer="Merge"
  data-type="Other"
  v-tooltip:right="'Merge'"
  v-tooltip-interactive:right="interactiveInfo"
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
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Math Merge',
        text: 'Merge layer.'
      }
    }
  }
}
</script>
