<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
  data-component="LearnClassRandomForest"
  data-layer="Random Forest"
  )
    i.icon.icon-

</template>

<script>
export default {
  name: 'ViewLearnClassRandomForest',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
