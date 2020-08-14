<template lang="pug">
  base-net-el(:dataEl="elementData")
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")
    

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-data-cloud.vue';
  import SettingsEl   from './set-data-cloud';

  export default {
    name: 'DataCloud',
    components: {
      BaseNetEl,
      ViewEl
    },
    props: {
      elementData: Object,
     withLayerTypeText: Boolean,
    },
  }
</script>
