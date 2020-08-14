<template lang="pug">
  base-net-el(:dataEl="elementData")
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")


</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-data-random';

  export default {
    name: 'DataRandom',
    components: {
      BaseNetEl,
      ViewEl,
    },
    props: {
      elementData: Object,
     withLayerTypeText: Boolean,
    },
  }
</script>
