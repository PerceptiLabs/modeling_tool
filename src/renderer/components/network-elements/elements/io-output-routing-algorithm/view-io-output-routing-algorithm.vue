<template lang="pug">
  .btn.btn--layersbar.net-element-io(:draggable="draggable"
  data-component="IoOutputRouting"
  data-layer="Routing Algorithm"
  )
    i.icon.icon-data-out

</template>

<script>
export default {
  name: 'ViewIoOutputRouting',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
