<template lang="pug">
  .btn.btn--layersbar.net-element-math(:draggable="draggable"
  data-component="MathSwitch"
  data-layer="Switch"
  data-type="Other"
  v-tooltip:networkElement="'Switch'"
  v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-switch

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewMathSwitch',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Math Switch',
        text: 'Switch layer'
      }
    }
  }
}
</script>
