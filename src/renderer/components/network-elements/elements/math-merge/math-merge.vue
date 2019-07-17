<template lang="pug">
  base-net-el(
  :dataEl="elementData"
  )
    view-el(:current-el="elementData")
    template(slot="settings")
      settings-el(:current-el="elementData")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-math-merge.vue';
  import SettingsEl   from './set-math-merge';

  export default {
    name: 'MathMerge',
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
