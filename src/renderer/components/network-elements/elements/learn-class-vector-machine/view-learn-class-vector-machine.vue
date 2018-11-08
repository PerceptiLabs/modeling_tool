<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
    data-component="LearnClassVectorMachine"
    data-layer="Support Vector Machine"
  data-type="Training"
  )
    i.icon.icon-round-figur2

</template>

<script>
export default {
  name: 'ViewLearnClassVectorMachine',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
