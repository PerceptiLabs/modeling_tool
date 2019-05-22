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
  import ViewEl       from './view-train-reinforce.vue';
  import SettingsEl   from './set-train-reinforce';

  export default {
    name: 'TrainReinforce',
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
