<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="false"  disabled="disabled"
    data-component="TrainReinforce"
    data-layer="Reinforcement Learning"
    data-type="Training"
    v-tooltip:right="'Training Reinforce'"
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
