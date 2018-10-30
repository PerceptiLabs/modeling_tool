<template lang="pug">
  base-net-el(
    :dataEl="elementData"
  )
    view-el
    template(slot="context")
      context-menu
    template(slot="settings")
      settings-el

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import ViewEl       from './view-train-reinforce.vue';
  import SettingsEl   from './set-train-reinforce';

  export default {
    name: 'TrainReinforce',
    components: {
      BaseNetEl,
      ContextMenu,
      ViewEl,
      SettingsEl
    },
    props: {
      elementData: Object
    },
  }
</script>
