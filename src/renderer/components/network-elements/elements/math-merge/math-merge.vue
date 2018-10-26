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
  import ViewEl       from './view-math-merge.vue';
  import SettingsEl   from './set-math-merge';

  export default {
    name: 'MathMerge',
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
