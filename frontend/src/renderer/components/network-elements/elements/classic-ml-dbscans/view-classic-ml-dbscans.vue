<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLDbscans"
    data-layer="DBSCAN"
    data-type="Training"
    v-tooltip:networkElement="'DBSCAN'"
    v-tooltip-interactive:right="interactiveInfo.MLDbscan"
    :style="layerStyles"
  )
    i.icon.icon-round-three
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
  name: 'ViewClassicMLDbscans',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        MLDbscan: {
          title: 'MLDbscan',
          text: 'Choose which method to use'
        }
      }
    }
  }
}
</script>
