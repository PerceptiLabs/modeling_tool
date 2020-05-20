<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataRandom"
    data-layer="Random"
    data-type="Data"
    v-tooltip:right="'Random'"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-random-data

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDataRandom',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Data Random',
        text: 'Read an Random either </br> from Gym or Unity'
      }
    }
  }
}
</script>
