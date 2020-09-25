<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessReshape"
    data-layer="Reshape"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_process-reshape"
    :style="layerStyles"
  )
    i.icon.icon-processing-group
    text-editable.layer-type(
      v-if="withLayerTypeText"
      :text-title="currentEl.layerName"
      @change-title="editElName"
      :styleType="['network-view']"
      )
    //- settings-preview(
    //-   :current-el="currentEl"
    //- )
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
  import TextEditable       from '@/components/base/text-editable.vue';
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
  import SettingsPreview  from "@/components/network-elements/elements-settings/setting-preview.vue";
export default {
  name: 'ViewProcessReshape',
  components: { SettingsPreview },
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Process Reshape',
        text: 'Reshape the data'
      },
      displayTitle: 'Reshape'
    }
  }
}
</script>
