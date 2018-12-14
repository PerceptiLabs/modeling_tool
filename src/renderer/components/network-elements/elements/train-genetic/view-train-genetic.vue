<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="false"  disabled="disabled"
  data-component="TrainGenetic"
  data-layer="Genetic Algorithm"
  data-type="Training"
  )
    i.icon.icon-learning-genetic

</template>

<script>
export default {
  name: 'ViewTrainGenetic',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
