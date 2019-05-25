<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainReinforce"
    data-layer="Reinforcement Learning"
    data-type="Training"
    v-tooltip:right="'Reinforcement Learning'"
  )
    i.icon.icon-learning-reinforcement1

</template>

<script>
export default {
  name: 'ViewTrainReinforce',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
