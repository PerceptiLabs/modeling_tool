<template lang="pug">
  //-:draggable="false"  disabled="disabled"
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathSplit"
  data-layer="Split"
  data-type="Other"
  v-tooltip:right="'Split'"
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
