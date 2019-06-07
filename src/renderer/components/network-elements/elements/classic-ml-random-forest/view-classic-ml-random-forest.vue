<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
  data-component="ClassicMLRandomForest"
  data-layer="Random Forest"
  data-type="Training"
  v-tooltip:right="'Random Forest'"
  v-tooltip-interactive:right="interactiveInfo.MLRandomForest"
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
  },
  data() {
    return {
      interactiveInfo: {
        MLRandomForest: {
          title: 'ML Random Forest',
          text: 'Random forest layer'
        }
      }
    }
  }
}
</script>
