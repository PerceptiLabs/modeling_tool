<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessRescale"
    data-layer="Rescale"
    data-type="Other"
    v-tooltip:right="'Rescale'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_process-rescale"
    :style="layerStyles"
  )
    i.icon.icon-full-screen

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewProcessRescale',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Process Rescale',
        text: 'Rescale the data'
      }
    }
  }
}
</script>
