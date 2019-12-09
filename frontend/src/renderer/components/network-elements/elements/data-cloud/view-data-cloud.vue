<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="DataCloud"
    data-layer="Cloud"
    data-type="Data"
    v-tooltip:right="'Cloud'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_data-data"
    :style="layerStyles"
  )
    i.icon.icon-data-cloud

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewDataCloud',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Cloud',
        text: 'Read local data or data from a server'
      }
    }
  }
}
</script>
