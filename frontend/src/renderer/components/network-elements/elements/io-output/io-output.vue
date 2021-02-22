<template lang="pug">
  base-net-el(:dataEl="elementData")
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-io-output.vue';
  import SettingsEl   from './set-io-output.vue';

  export default {
    name: 'IoOutput',
    components: {
      BaseNetEl,
      ViewEl,
      SettingsEl
    },
    props: {
      elementData: Object,
      withLayerTypeText: Boolean,
    },
  }
</script>
