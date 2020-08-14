<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLRandomForest"
    data-layer="Random Forest"
    data-type="Training"
    v-tooltip:networkElement="'Random Forest'"
    v-tooltip-interactive:right="interactiveInfo.MLRandomForest"
    :style="layerStyles"
  )
    i.icon.icon-trees
    text-editable.layer-type(
      v-if="withLayerTypeText"
      :text-title="currentEl.layerName"
      @change-title="editElName"
      :styleType="['network-view']"
      )
</template>

<script>
  import mixinSet from '@/core/mixins/net-element-view-layer.js';
  import TextEditable       from '@/components/base/text-editable.vue';
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
export default {
  name: 'ViewClassicMLRandomForest',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        MLRandomForest: {
          title: 'ML Random Forest',
          text: 'Random forest layer'
        }
      }
    }
  }
}
</script>
