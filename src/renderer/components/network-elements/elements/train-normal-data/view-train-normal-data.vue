<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="false"  disabled="disabled"
    data-component="TrainNormalData"
    data-layer="Normal + Data"
    data-type="Training"
    v-tooltip:right="'Normal + Data'"
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
