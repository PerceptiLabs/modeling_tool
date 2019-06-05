<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
  data-component="TrainGenetic"
  data-layer="Genetic Algorithm"
  data-type="Training"
  v-tooltip:right="'Genetic Algorithm'"
  v-tooltip-interactive:right="interactiveInfo"
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
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Train GA',
        text: 'Genetic algorithm layer'
      }
    }
  }
}
</script>
