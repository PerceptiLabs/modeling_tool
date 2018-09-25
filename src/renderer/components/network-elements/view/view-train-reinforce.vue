<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
  data-component="TrainReinforce"
  data-layer="Reinforcement Learning"
  )
    i.icon.icon-

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
