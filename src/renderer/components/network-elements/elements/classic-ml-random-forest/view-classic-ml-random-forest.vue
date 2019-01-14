<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false"  disabled="disabled"
  data-component="ClassicMLRandomForest"
  data-layer="Random Forest"
  data-type="Training"
  v-tooltip:right="'Random'"
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
