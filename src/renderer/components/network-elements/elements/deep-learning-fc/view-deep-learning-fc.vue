<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
  data-component="DeepLearningFC"
  data-layer="FullyConnected_1"
  data-type="Other"
  )
    i.icon.icon-round

</template>

<script>
export default {
  name: 'ViewDeepLearningFC',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
