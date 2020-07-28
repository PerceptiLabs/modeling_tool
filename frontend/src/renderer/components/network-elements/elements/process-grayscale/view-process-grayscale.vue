<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessGrayscale"
    data-layer="Grayscale"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-sieve
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewProcessGrayscale',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Process Grayscale',
        text: 'Convert data to grayscale'
      },
      displayTitle: 'Grayscale'
    }
  }
}
</script>
