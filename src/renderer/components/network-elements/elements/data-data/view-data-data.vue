<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataData"
    data-layer="Data_1"
    data-type="Data"
    v-tooltip:right="'Data'"
    v-tooltip-interactive:right="interactiveInfo"
    id="tutorial_data-data"
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
  },
  data() {
    return {
      interactiveInfo: {
        title: 'Data',
        text: 'Read local data or data from a server'
      }
    }
  }
}
</script>
