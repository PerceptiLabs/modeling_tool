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
  import ViewEl       from './view-classic-ml-dbscans.vue';
  import SettingsEl   from './set-classic-ml-dbscans.vue';

  export default {
    name: 'ClassicMLDbscans',
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
