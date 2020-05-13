<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataData"
    data-layer="Data"
    data-type="Data"
    v-tooltip:networkElement="'Data'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_data-data"
    :style="layerStyles"
  )
    i.icon.icon-data

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDataData',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Data',
        text: 'Read local data or data from a server'
      }
    }
  }
}
</script>
