<template lang="pug">
  base-net-el
    view-el
    template(slot="context")
      context-menu

</template>

<script>
import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
import ViewEl       from '@/components/network-elements/view/view-io-input.vue';
//import netElement   from '@/core/mixins/net-element.js';

export default {
  name: 'IoInput',
  components: {
    BaseNetEl,
    ContextMenu,
    ViewEl
  },
  //mixins: [netElement],
  props: {
    elementData: Object
  },
  mounted() {
    console.log(this.elementData)
  },
  provide: {
    dataEl: this.elementData
  },
}
</script>

