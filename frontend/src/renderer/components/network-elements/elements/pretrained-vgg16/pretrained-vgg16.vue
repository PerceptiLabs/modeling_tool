<template lang="pug">
  base-net-el(
    :data-el="elementData"
  )
    view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-pretrained-vgg16.vue';

  export default {
    name: 'PreTrainedVGG16',
    components: {
      BaseNetEl,
      ViewEl,
    },
    props: {
      elementData: Object,
      withLayerTypeText: Boolean,
    },
  }
</script>
