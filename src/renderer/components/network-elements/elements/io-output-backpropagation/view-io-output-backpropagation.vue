<template lang="pug">
  .btn.btn--layersbar.net-element-io(:draggable="draggable"
  data-component="IoOutputBackprop"
  data-layer="Backpropagation"
  )
    i.icon.icon-data-out

</template>

<script>
export default {
  name: 'ViewIoInput',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
