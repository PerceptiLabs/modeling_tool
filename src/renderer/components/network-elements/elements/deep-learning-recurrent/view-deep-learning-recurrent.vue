<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningRecurrent"
    data-layer="Recurrent"
    data-type="Other"
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
  }
}
</script>
