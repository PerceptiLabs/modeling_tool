<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningConv"
    data-layer="Convolution_1"
    data-type="Other"
    v-tooltip:right="'Convolution'"
    id="tutorial_convolution"
  )
    i.icon.icon-round-out

</template>

<script>
export default {
  name: 'ViewDeepLearningConv',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
