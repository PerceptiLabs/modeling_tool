<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessRescale"
    data-layer="Rescale"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_process-rescale"
    :style="layerStyles"
  )
    i.icon.icon-full-screen
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
  name: 'ViewProcessRescale',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Process Rescale',
        text: 'Rescale the data'
      },
      displayTitle: 'Rescale'
    }
  }
}
</script>
