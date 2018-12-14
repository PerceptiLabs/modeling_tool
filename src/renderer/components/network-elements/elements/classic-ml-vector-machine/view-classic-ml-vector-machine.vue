<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="false"  disabled="disabled"
    data-component="ClassicMLSVM"
    data-layer="Support Vector Machine"
    data-type="Training"
  )
    i.icon.icon-round-figur2

</template>

<script>
export default {
  name: 'ViewClassicMLSVM',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
