<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathSoftmax"
  data-layer="Softmax"
  data-type="Other"
  v-tooltip:networkElement="'Softmax'"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-calc-softmax

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewMathSoftmax',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Math Softmax',
        text: 'Softmax layer'
      }
    }
  }
}
</script>
