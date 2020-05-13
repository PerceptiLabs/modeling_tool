<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataEnvironment"
    data-layer="Environment"
    data-type="Data"
    v-tooltip:networkElement="'Environment'"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-map

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDataEnvironment',
  mixins: [mixinSet],
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
