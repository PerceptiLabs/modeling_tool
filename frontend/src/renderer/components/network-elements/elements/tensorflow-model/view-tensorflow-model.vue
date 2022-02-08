<template lang="pug">
.btn.btn--layersbar.net-element-learn-deep(
  :draggable="draggable",
  data-component="LayerTfModel",
  data-layer="LayerTfModel",
  data-type="Other",
  v-tooltip-interactive:right="interactiveInfo",
  :style="layerStyles"
)
  i.icon.icon-deep-learning-group
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
import mixinFocus from "@/core/mixins/net-element-settings-input-focus.js";
import TextEditable from "@/components/base/text-editable.vue";

export default {
  name: "ViewLayerTfModel",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: "Tensorflow Model",
        text: "Tensorflow Model"
      },
      displayTitle: "Tensorflow Model"
    };
  }
};
</script>
