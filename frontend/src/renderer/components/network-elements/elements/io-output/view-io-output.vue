<template lang="pug">
#tutorial_io-output.btn.btn--layersbar.net-element-train(
  :draggable="draggable",
  data-component="IoOutput",
  data-layer="IO_Output",
  data-type="IoOutput",
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
  img.icon-lock(
    src="../../../../../../static/img/lock2.svg",
  )
</template>

<script>
import mixinSet from "@/core/mixins/net-element-view-layer.js";
import TextEditable from "@/components/base/text-editable.vue";
import mixinFocus from "@/core/mixins/net-element-settings-input-focus.js";
export default {
  name: "ViewIoOutput",
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
    withLayerTypeText: Boolean
  },
  data() {
    return {
      interactiveInfo: {
        title: "IO Output",
        text: "Read local CSV data "
      },
      displayTitle: "IO Output"
    };
  }
};
</script>
<style lang="scss" scoped>
.btn--layersbar .icon-lock {
  text-shadow: none;
}
.icon-lock {
  // opacity: 0.7;
  margin-left: 8px;

  .dark-theme & {
    filter: invert(80%);
  }

  .net-element--active & {
    filter: none;
  }
}
</style>
