<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
  data-component="LearnClassDbscans"
  data-layer="DBSCAN"
  data-type="Training"
  )
    i.icon.icon-round-three

</template>

<script>
export default {
  name: 'ViewLearnClassDbscans',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
