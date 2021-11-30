<template lang="pug">
#tutorial_one-hot.btn.btn--layersbar.net-element-process(
  :draggable="draggable",
  data-component="ProcessOneHot",
  data-layer="OneHot",
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
  name: "ViewProcessOneHot",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: "Process OneHot",
        text: "Use one hot encoding"
      },
      displayTitle: "OneHot"
    };
  }
};
</script>
