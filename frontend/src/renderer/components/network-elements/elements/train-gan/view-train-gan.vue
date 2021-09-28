<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainGan"
    data-layer="GAN"
    data-type="Training"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_training-gan"
    :style="layerStyles"
  )
    i.icon.icon-train-group
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
  name: 'ViewTrainGan',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Train GAN',
        text: ''
      },
      displayTitle: 'GAN'
    }
  }
}
</script>
<style lang="scss" scoped>
  
  .icon {
    transform: translateX(3px);
  }
</style>
