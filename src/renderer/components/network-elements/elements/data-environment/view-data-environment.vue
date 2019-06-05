<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataEnvironment"
    data-layer="Environment"
    data-type="Data"
    v-tooltip:right="'Environment'"
    v-tooltip-interactive:right="interactiveInfo"
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
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Data Environment',
        text: 'Read an environment either </br> from Gym or Unity'
      }
    }
  }
}
</script>
