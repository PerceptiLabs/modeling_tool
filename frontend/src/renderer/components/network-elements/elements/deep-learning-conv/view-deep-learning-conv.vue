<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="DeepLearningConv"
    data-layer="Convolution"
    data-type="Other"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_convolution"
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
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
  import TextEditable       from '@/components/base/text-editable.vue';
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
export default {
  name: 'ViewDeepLearningConv',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Deep Learning Conv',
        text: 'Convolutional layer'
      },
      displayTitle: 'Convolution'
    }
  }
}
</script>
