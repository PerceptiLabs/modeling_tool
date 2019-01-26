<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false"  disabled="disabled"
    data-component="ClassicMLKMeans"
    data-layer="K-Means Clustering"
    data-type="Training"
    v-tooltip:right="'K-Means Clustering'"
  )
    i.icon.icon-round-sieve

</template>

<script>
export default {
  name: 'ViewClassicMLKMeans',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
