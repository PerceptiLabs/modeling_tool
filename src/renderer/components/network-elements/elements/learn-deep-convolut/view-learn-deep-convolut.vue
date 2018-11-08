<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
  data-component="LearnDeepConvolut"
  data-layer="Convolution"
  data-type="Other"
  )
    i.icon.icon-round-out

</template>

<script>
export default {
  name: 'ViewLearnDeepConvolut',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
