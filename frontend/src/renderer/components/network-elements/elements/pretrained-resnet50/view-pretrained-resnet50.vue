<template lang="pug">
.btn.btn--layersbar.net-element-learn-deep(
  :draggable="draggable",
  data-component="PreTrainedResNet50",
  data-layer="ResNet50",
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
  name: "ViewPreTrainedResNet50",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: "Deep Learning ResNet50",
        text: "Pretrained ResNet50"
      },
      displayTitle: "ResNet50"
    };
  }
};
</script>
