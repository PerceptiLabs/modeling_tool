<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessReshape"
    data-layer="Reshape"
    data-type="Other"
    v-tooltip:right="'Reshape'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_process-reshape"
  )
    i.icon.icon-full-screen

</template>

<script>
export default {
  name: 'ViewProcessReshape',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  },
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
