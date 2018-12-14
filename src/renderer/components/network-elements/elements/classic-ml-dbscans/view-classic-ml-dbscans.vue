<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false"  disabled="disabled"
    data-component="ClassicMLDbscans"
    data-layer="DBSCAN"
    data-type="Training"
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
