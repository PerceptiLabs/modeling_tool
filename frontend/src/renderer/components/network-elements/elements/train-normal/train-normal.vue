<template lang="pug">
base-net-el(:data-el="elementData")
  view-el(:current-el="elementData", :withLayerTypeText="withLayerTypeText")
</template>

<script>
import BaseNetEl from "@/components/network-elements/net-base-element/net-base-element.vue";
import ViewEl from "./view-train-normal.vue";

export default {
  name: "TrainNormal",
  components: {
    BaseNetEl,
    ViewEl
  },
  props: {
    elementData: Object,
    withLayerTypeText: Boolean
  }
};
</script>
