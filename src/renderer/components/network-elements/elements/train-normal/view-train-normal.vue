<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainNormal"
    data-layer="Normal"
    data-type="Training"
    v-tooltip:right="'Normal'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_training-normal"
  )
    i.icon.icon-training

</template>

<script>
export default {
  name: 'ViewTrainNormal',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Train Normal',
        text: 'Normal supervised learning layer'
      }
    }
  }
}
</script>
