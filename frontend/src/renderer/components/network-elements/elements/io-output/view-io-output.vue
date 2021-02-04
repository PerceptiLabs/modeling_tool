<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="IoOutput"
    data-layer="IO_Output"
    data-type="Data"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_io-output"
    :style="layerStyles"
  )
    i.icon.icon-train-group
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
  name: 'ViewIoOutput',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'IO Output',
        text: 'Read local CSV data '
      },
      displayTitle: 'IO Output'
    }
  }
}
</script>
