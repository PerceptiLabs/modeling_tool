<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLKMeans"
    data-layer="K-Means Clustering"
    data-type="Training"
    v-tooltip:networkElement="'K-Means Clustering'"
    v-tooltip-interactive:right="interactiveInfo.MLKmeans"
    :style="layerStyles"
  )
    i.icon.icon-round-sieve
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
  name: 'ViewClassicMLKMeans',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        MLKmeans: {
          title: 'MLKmeans',
          text: 'K means clustering layer.'
        }
      }
    }
  }
}
</script>
