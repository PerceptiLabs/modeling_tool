<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessGrayscale"
    data-layer="Grayscale"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-sieve
    text-editable.layer-type(
      v-if="withLayerTypeText"
      :text-title="currentEl.layerName"
      @change-title="editElName"
      :styleType="['network-view']"
      )
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
  import TextEditable       from '@/components/base/text-editable.vue';
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
export default {
  name: 'ViewProcessGrayscale',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Process Grayscale',
        text: 'Convert data to grayscale'
      },
      displayTitle: 'Grayscale'
    }
  }
}
</script>
