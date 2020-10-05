<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataRandom"
    data-layer="Random"
    data-type="Data"
    v-tooltip-interactive:right="interactiveInfo"
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
import mixinSet from "@/core/mixins/net-element-view-layer.js";
import TextEditable       from '@/components/base/text-editable.vue';
import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
export default {
  name: "ViewDataRandom",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Data Random',
        text: 'Generate random data of a specified shape'
      },
      displayTitle: 'Random'
    }
  }
};
</script>
