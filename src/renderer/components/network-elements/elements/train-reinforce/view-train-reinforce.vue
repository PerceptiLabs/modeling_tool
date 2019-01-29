<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="true"
    data-component="TrainReinforce"
    data-layer="Reinforcement Learning"
    data-type="Training"
    v-tooltip:right="'Training Reinforce'"
  )
    i.icon.icon-learning-reinforcement

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
