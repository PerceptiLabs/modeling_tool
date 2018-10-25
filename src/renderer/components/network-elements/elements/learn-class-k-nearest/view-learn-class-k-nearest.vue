<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
  data-component="LearnClassKNearest"
  data-layer="K Nearest Neighbor"
  )
    i.icon.icon-round-figur

</template>

<script>
export default {
  name: 'ViewLearnClassKNearest',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
