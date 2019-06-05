<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningRecurrent"
    data-layer="Recurrent"
    data-type="Other"
    v-tooltip:right="'Recurrent'"
    v-tooltip-interactive:right="interactiveInfo"
  )
    i.icon.icon-round-left

</template>

<script>
export default {
  name: 'ViewDeepLearningRecurrent',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Deep Learning Recurrent',
        text: 'Recurrent layer'
      }
    }
  }
}
</script>
