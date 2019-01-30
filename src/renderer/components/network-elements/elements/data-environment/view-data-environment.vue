<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="true"
    data-component="DataEnvironment"
    data-layer="Environment"
    data-type="Data"
    v-tooltip:right="'Environment'"
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
