<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessResize"
    data-layer="Resize"
    data-type="Other"
    v-tooltip:right="'Resize'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_process-resize"
    :style="layerStyles"
  )
    i.icon.icon-full-screen

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewProcessResize',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Process Resize',
        text: 'Resize the data'
      }
    }
  }
}
</script>
