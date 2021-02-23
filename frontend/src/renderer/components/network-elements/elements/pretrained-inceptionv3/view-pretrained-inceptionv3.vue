<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
    data-component="PreTrainedInceptionV3"
    data-layer="InceptionV3"
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
    name: 'ViewPreTrainedInceptionV3',
    mixins: [ mixinSet, mixinFocus ],
    components: { TextEditable },
    props: {
        withLayerTypeText: Boolean,
    },
    data() {
      return {
        interactiveInfo: {
          title: 'Pretrained InceptionV3',
          text: 'Pretrained InceptionV3'
        },
        displayTitle: 'InceptionV3'
      }
    }
  }
</script>
