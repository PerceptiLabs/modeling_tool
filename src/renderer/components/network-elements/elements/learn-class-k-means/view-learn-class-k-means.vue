<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
    data-component="LearnClassKMeans"
    data-layer="K-Means Clustering"
  data-type="Training"
  )
    i.icon.icon-round-sieve

</template>

<script>
export default {
  name: 'ViewLearnClassKMeans',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
