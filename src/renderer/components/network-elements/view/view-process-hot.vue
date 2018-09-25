<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessHot"
  data-layer="One Hot"
  )
    i.icon.icon-

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
