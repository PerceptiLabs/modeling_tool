<template lang="pug">
button.btn.btn--layersbar.net-element-math(
  type="button",
  :draggable="draggable",
  data-component="MathMerge",
  data-layer="Merge",
  data-type="Other",
  v-tooltip-interactive:right="interactiveInfo",
  :style="layerStyles"
)
  i.icon.icon-math-group
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
  name: "ViewMathMerge",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: "Math Merge",
        text: "Merge layer."
      },
      displayTitle: "Merge"
    };
  }
};
</script>
