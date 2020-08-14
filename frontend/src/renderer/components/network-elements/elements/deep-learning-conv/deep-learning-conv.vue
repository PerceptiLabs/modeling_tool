<template lang="pug">
  base-net-el(:data-el="elementData")
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")
    //- template(slot="settings")
    //-   settings-el(:current-el="elementData")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-deep-learning-conv.vue';
  // import SettingsEl   from './set-deep-learning-conv.vue';

  export default {
    name: 'DeepLearningConv',
    components: {
      BaseNetEl,
      ViewEl,
      // SettingsEl
    },
    props: {
      elementData: Object,
     withLayerTypeText: Boolean,
    },
  }
</script>
