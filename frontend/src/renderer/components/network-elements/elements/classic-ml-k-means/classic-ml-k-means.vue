<template lang="pug">
  base-net-el(
    :data-el="elementData"
  )
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")
    

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-classic-ml-k-means.vue';
  import SettingsEl   from './set-classic-ml-k-means.vue';

  export default {
    name: 'ClassicMLKMeans',
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
