<template lang="pug">
  base-net-el(:dataEl="elementData")
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-io-input.vue';
  import SettingsEl   from './set-io-input.vue';

  export default {
    name: 'IoInput',

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
