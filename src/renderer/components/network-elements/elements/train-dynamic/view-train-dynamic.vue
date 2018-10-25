<template lang="pug">
  .btn.btn--layersbar.net-element-train(:draggable="draggable"
    data-component="TrainDynamic"
    data-layer="Dynamic Routing"
  )
    i.icon.icon-learning-dynamic

</template>

<script>
export default {
  name: 'ViewTrainDynamic',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
