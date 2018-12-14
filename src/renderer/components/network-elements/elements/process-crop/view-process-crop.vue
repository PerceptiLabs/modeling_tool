<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="false"  disabled="disabled"
  data-component="ProcessCrop"
  data-layer="Crop"
  data-type="Other"
  v-tooltip="'Crop'"
  )
    i.icon.icon-crop-symbol

</template>

<script>
export default {
  name: 'ViewProcessCrop',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
