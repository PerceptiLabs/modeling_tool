<template lang="pug">
  button.btn.btn--layersbar.net-element-math(type="button" :draggable="draggable"
  data-component="DataData"
  data-layer="Data"
  )
    i.icon.icon-data

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
