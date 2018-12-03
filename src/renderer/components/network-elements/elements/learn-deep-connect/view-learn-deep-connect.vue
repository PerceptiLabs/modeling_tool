<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
  data-component="LearnDeepConnect"
  data-layer="FullyConnected_1"
  data-type="Other"
  v-tooltip="'Fully Connected'"
  )
    i.icon.icon-round

</template>

<script>
export default {
  name: 'ViewDataData',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
