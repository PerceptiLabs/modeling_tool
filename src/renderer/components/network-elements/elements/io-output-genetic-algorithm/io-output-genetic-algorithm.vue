<template lang="pug">
  base-net-el(
    :dataEl="elementData"
  )
    view-el
    template(slot="context")
      context-menu

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import ViewEl       from './view-io-output-genetic-algorithm.vue';

  export default {
    name: 'IoOutputGenetic',
    components: {
      BaseNetEl,
      ContextMenu,
      ViewEl
    },
    props: {
      elementData: Object
    },
  }
</script>
