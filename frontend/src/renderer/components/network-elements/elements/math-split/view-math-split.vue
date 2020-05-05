<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="MathSplit"
    data-layer="Split"
    data-type="Other"
    v-tooltip:bottom="'Split'"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-road-split

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewMathSplit',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Math Split',
        text: 'Split layer'
      }
    }
  }
}
</script>
