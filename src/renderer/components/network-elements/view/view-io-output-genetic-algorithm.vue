<template lang="pug">
  .btn.btn--layersbar.net-element-io(:draggable="draggable"
  data-component="IoOutputGenetic"
  data-layer="Genetic Algorithm"
  )
    i.icon.icon-data-out

</template>

<script>
export default {
  name: 'ViewIoOutputGenetic',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
