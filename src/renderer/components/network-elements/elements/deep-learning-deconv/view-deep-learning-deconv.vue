<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
  data-component="DeepLearningDeconv"
  data-layer="Deconvolution_1"
  data-type="Other"
  v-tooltip:right="'Deconvolution'" 
  )
    i.icon.icon-round-in

</template>

<script>
export default {
  name: 'ViewDeepLearningDeconv',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
