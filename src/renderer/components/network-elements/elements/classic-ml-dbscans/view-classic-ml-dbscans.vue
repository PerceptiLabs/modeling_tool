<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
    data-component="ClassicMLDbscans"
    data-layer="DBSCAN"
    data-type="Training"
    v-tooltip:right="'DBSCAN'"
  )
    i.icon.icon-round-three

</template>

<script>
export default {
  name: 'ViewClassicMLDbscans',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
