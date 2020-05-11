<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessReshape"
    data-layer="Reshape"
    data-type="Other"
    v-tooltip:bottom="'Reshape'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_process-reshape"
    :style="layerStyles"
  )
    i.icon.icon-full-screen

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewProcessReshape',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Process Reshape',
        text: 'Reshape the data'
      }
    }
  }
}
</script>
