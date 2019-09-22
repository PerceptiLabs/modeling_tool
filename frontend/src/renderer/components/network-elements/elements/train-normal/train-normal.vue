<template lang="pug">
  base-net-el(
    :data-el="elementData"
  )
    view-el(:current-el="elementData")
    template(slot="settings")
      settings-el(:current-el="elementData")
</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-train-normal.vue';
  import SettingsEl   from './set-train-normal';

  export default {
    name: 'TrainNormal',
    components: {
      BaseNetEl,
      ViewEl,
      SettingsEl
    },
    props: {
      elementData: Object
    },
  }
</script>
