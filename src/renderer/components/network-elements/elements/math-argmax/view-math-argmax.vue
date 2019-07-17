<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathArgmax"
  data-layer="Argmax_1"
  data-type="Other"
  v-tooltip:right="'Argmax'"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-l-calc-argmax

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewMathArgmax',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Math Argmax',
        text: 'Argmax layer'
      }
    }
  }
}
</script>
