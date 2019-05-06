<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
  data-component="ClassicMLKNN"
  data-layer="K Nearest Neighbor"
  data-type="Training"
  v-tooltip:right="'K Nearest Neighbor'"
  )
    i.icon.icon-round-figur

</template>

<script>
export default {
  name: 'ViewClassicMLKNN',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
