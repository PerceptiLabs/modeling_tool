<template lang="pug">
  .btn.btn--layersbar.net-element-io(:draggable="draggable"
  data-component="IoInput"
  data-layer="Input"
  )
    i.icon.icon-data-in

</template>

<script>
export default {
  name: 'ViewIoOutput',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
