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
  import ViewEl       from '@/components/network-elements/view/view-process-hot.vue';
  //import netElement   from '@/core/mixins/net-element.js';

  export default {
    name: 'ProcessHot',
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
