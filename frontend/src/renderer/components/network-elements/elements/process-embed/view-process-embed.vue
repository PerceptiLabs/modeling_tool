<template lang="pug">
.btn.btn--layersbar.net-element-process(
  :draggable="draggable",
  data-component="ProcessEmbed",
  data-layer="Word Embedding",
  data-type="Other",
  v-tooltip-interactive:right="interactiveInfo",
  :style="layerStyles"
)
  i.icon.icon-processing-group
  text-editable.layer-type(
    v-if="withLayerTypeText",
    :text-title="currentEl.layerName",
    @change-title="editElName",
    :styleType="['network-view']"
  )
  .layerTitle(v-if="showTitle") {{ displayTitle }}
</template>

<script>
import mixinSet from "@/core/mixins/net-element-view-layer.js";
import TextEditable from "@/components/base/text-editable.vue";
import mixinFocus from "@/core/mixins/net-element-settings-input-focus.js";
export default {
  name: "ViewProcessEmbed",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: "Process WordEmbedding",
        text: "Use word embedding"
      },
      displayTitle: "Embedding"
    };
  }
};
</script>
