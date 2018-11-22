<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessHot"
  data-layer="One Hot"
  data-type="Other"
  v-tooltip="'One Hot'"
  )
    i.icon.icon-one-hot

</template>

<script>
export default {
  name: 'ViewProcessHot',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
