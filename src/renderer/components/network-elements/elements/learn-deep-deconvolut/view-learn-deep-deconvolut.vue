<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
  data-component="LearnDeepDeconvolut"
  data-layer="Deconvolution"
  data-type="Other"
  v-tooltip="'Deconvolution'"
  )
    i.icon.icon-round-in

</template>

<script>
export default {
  name: 'ViewLearnDeepDeconvolut',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
