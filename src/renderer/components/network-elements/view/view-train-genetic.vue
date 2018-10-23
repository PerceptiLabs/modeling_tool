<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
  data-component="TrainGenetic"
  data-layer="Genetic Algorithm"
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
