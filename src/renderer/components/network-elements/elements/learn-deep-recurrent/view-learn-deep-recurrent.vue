<template lang="pug">
  .btn.btn--layersbar.net-element-learn-deep(:draggable="draggable"
  data-component="LearnDeepRecurrent"
  data-layer="Recurrent"
  data-type="Other"
  )
    i.icon.icon-round-left

</template>

<script>
export default {
  name: 'ViewLearnDeepRecurrent',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
