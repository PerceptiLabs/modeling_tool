<template lang="pug">
  button.btn.btn--layersbar.net-element-math(type="button" :draggable="draggable"
  data-component="MathMerge"
  data-layer="Merge"
  data-type="Other"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-road-concat
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewMathMerge',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Math Merge',
        text: 'Merge layer.'
      },
      displayTitle: 'Merge'
    }
  }
}
</script>
