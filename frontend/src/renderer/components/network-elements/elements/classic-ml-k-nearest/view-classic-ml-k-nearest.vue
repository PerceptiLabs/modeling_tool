<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLKNN"
    data-layer="K Nearest Neighbor"
    data-type="Training"
    v-tooltip:networkElement="'K Nearest Neighbor'"
    v-tooltip-interactive:right="interactiveInfo.MLKnn"
    :style="layerStyles"
  )
    i.icon.icon-round-figur
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
  name: 'ViewClassicMLKNN',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        MLKnn: {
          title: 'MLKnn',
          text: 'K Nearest neighbors layer'
        }
      }
    }
  }
}
</script>
