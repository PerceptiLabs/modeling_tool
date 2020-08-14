<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="ClassicMLSVM"
    data-layer="Support Vector Machine"
    data-type="Training"
    v-tooltip:networkElement="'Support Vector Machine'"
    v-tooltip-interactive:right="interactiveInfo.MLSvm"
    :style="layerStyles"
  )
    i.icon.icon-round-figur2
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
  name: 'ViewClassicMLSVM',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        MLSvm: {
          title: 'MLSvm',
          text: 'SVM layer'
        }
      }
    }
  }
}
</script>
