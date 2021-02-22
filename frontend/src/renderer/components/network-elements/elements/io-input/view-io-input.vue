<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="IoInput"
    data-layer="IO_Input"
    data-type="IoInput"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_data-data"
    :style="layerStyles"
  )
    i.icon.icon-data
    text-editable.layer-type(
      v-if="withLayerTypeText"
      :text-title="currentEl.layerName"
      @change-title="editElName"
      :styleType="['network-view']"
      )
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet     from '@/core/mixins/net-element-view-layer.js';
  import TextEditable from '@/components/base/text-editable.vue';
  import mixinFocus   from '@/core/mixins/net-element-settings-input-focus.js';
export default {
  name: 'ViewIoInput',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Data IO Input',
        text: 'Read local CSV data '
      },
      displayTitle: 'IO Input'
    }
  }
}
</script>
