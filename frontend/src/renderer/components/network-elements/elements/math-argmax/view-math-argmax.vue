<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathArgmax"
  data-layer="Argmax"
  data-type="Other"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-l-calc-argmax
    .layerTitle(v-if="showTitle") {{ displayTitle }}

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
      },
      displayTitle: 'Argmax'
    }
  }
}
</script>
