<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
  data-component="ClassicMLRandomForest"
  data-layer="Random Forest"
  data-type="Training"
  v-tooltip:right="'Random Rorest'"
  )
    i.icon.icon-trees

</template>

<script>
export default {
  name: 'ViewClassicMLRandomForest',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
