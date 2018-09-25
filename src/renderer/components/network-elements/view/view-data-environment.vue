<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
  data-component="DataEnvironment"
  data-layer="Environment"
  )
    i.icon.icon-map

</template>

<script>
export default {
  name: 'ViewDataEnvironment',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
