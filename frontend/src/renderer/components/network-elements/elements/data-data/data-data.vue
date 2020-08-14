<template lang="pug">
  base-net-el(:dataEl="elementData")
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-data-data.vue';
  import SettingsElWeb   from './set-data-data';
  import SettingsElElectron   from './set-data-data-electron';

  let SettingsEl = null;
  if(!(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1)) {
    SettingsEl = SettingsElWeb;
  } else {
    SettingsEl = SettingsElElectron
  }
  export default {
    name: 'DataData',

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
