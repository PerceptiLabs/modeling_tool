<template lang="pug">
  base-net-el(
    :dataEl="elementData"
    :layerContainer="true"
    @dblcl="openChild"
  )
    view-el
    template(slot="context")
      context-menu

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import ViewEl       from './view-layer-container.vue';

  export default {
    name: 'LayerContainer',
    components: {
      BaseNetEl,
      ContextMenu,
      ViewEl
    },
    props: {
      elementData: Object
    },
    methods: {
      openChild() {
        this.$store.commit('mod_workspace/SHOW_layerContainer', this.elementData.index);
      }
    }
  }
</script>
