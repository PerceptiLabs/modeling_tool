<template lang="pug">
  base-net-el(
    :data-el="elementData"
  )
    view-el
    template(slot="settings")
      settings-el(:current-el="elementData")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-train-genetic.vue';
  import SettingsEl   from './set-train-genetic';

  export default {
    name: 'TrainGenetic',
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
