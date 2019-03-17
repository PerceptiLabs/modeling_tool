<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessOneHot"
  data-layer="OneHot_1"
  data-type="Other"
  v-tooltip:right="'One Hot'"
  class="tutorial_one-hot tutorial_layersbar"
  )
    i.icon.icon-one-hot

</template>

<script>
export default {
  name: 'ViewProcessOneHot',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  }
}
</script>
