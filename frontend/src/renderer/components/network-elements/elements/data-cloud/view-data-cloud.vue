<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="false" :disabled="true"
    v-coming-soon="true"
    data-component="DataCloud"
    data-layer="Cloud"
    data-type="Data"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_data-data"
    :style="layerStyles"
  )
    i.icon.icon-data-cloud
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
  name: 'ViewDataCloud',
  mixins: [mixinSet, mixinFocus],
  components: { TextEditable },
  props: {
      withLayerTypeText: Boolean,
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Cloud',
        text: 'Read local data or data from a server'
      }
    }
  }
}
</script>
