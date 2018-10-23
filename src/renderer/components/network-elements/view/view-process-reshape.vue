<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessReshape"
  data-layer="Reshape"
  )
    i.icon.icon-full-screen

</template>

<script>
export default {
  name: 'ViewProcessReshape',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
