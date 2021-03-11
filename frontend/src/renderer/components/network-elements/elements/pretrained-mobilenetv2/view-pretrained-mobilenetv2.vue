<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="PreTrainedMobileNetV2"
    data-layer="MobileNetV2"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    :style="layerStyles"
  )
    i.icon.icon-deep-learning-group
    text-editable.layer-type(
      v-if="withLayerTypeText"
      :text-title="currentEl.layerName"
      @change-title="editElName"
      :styleType="['network-view']"
      )
    .layerTitle(v-if="showTitle") {{ displayTitle }}

</template>

<script>
  import mixinSet     from '@/core/mixins/net-element-view-layer.js';
  import mixinFocus   from '@/core/mixins/net-element-settings-input-focus.js';
  import TextEditable from '@/components/base/text-editable.vue';

  export default {
    name: 'ViewPreTrainedMobileNetV2',
    mixins: [ mixinSet, mixinFocus ],
    components: { TextEditable },
    props: {
        withLayerTypeText: Boolean,
    },
    data() {
      return {
        interactiveInfo: {
          title: 'Deep Learning MobileNetV2',
          text: 'Pretrained MobileNetV2'
        },
        displayTitle: 'MobileNetV2'
      }
    }
  }
</script>
