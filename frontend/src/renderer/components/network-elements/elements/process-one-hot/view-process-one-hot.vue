<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessOneHot"
  data-layer="OneHot"
  data-type="Other"
  v-tooltip:networkElement="'One Hot'"
  v-tooltip-interactive:right="interactiveInfo"
  id="tutorial_one-hot"
    :style="layerStyles"
  )
    i.icon.icon-one-hot

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
export default {
  name: 'ViewProcessOneHot',
  mixins: [mixinSet],
  data() {
    return {
      interactiveInfo: {
        title: 'Process OneHot',
        text: 'Use one hot encoding'
      }
    }
  }
}
</script>
