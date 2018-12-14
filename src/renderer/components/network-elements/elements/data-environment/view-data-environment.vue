<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="false"  disabled="disabled"
    data-component="DataEnvironment"
    data-layer="Environment"
    data-type="Data"
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
