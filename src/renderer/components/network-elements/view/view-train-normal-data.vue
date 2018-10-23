<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainNormalData"
    data-layer="Normal + Data"
  )
    i.icon.icon-l-learn-normData

</template>

<script>
export default {
  name: 'ViewTrainNormalData',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
