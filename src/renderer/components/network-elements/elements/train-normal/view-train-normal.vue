<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainNormal"
    data-layer="Normal"
    data-type="Training"
  v-tooltip="'Normal'"
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
  }
}
</script>
