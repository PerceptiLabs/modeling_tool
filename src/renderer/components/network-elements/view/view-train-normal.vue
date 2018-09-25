<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
  data-component="TrainNormal"
  data-layer="Normal"
  )
    i.icon.icon-data

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
