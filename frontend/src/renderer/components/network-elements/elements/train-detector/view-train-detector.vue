<template lang="pug">
#tutorial_training-detector.btn.btn--layersbar.net-element-train(
  :draggable="draggable",
  data-component="TrainDetector",
  data-layer="Object Detection",
  data-type="Training",
  v-tooltip-interactive:right="interactiveInfo",
  :style="layerStyles"
)
  i.icon.icon-train-group
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
  name: "ViewTrainDetector",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: "Train Detector",
        text: "Detector supervised learning layer"
      },
      displayTitle: "Object Detection"
    };
  }
};
</script>
