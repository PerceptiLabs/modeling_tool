<template lang="pug">
  base-net-el(
    :data-el="elementData"
  )
    view-el
    template(slot="context")
      context-menu
    template(slot="settings")
      settings-el(:current-el="elementData")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import ViewEl       from './view-classic-ml-k-means.vue';
  import SettingsEl   from './set-classic-ml-k-means.vue';

  export default {
    name: 'ClassicMLKMeans',
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
