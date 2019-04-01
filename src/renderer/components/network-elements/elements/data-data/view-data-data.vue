<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataData"
    data-layer="Data_1"
    data-type="Data"
    v-tooltip:right="'Data'"
    id="tutorial_data-data"
  )
    i.icon.icon-data

</template>

<script>
import { mapGetters }       from 'vuex';
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
