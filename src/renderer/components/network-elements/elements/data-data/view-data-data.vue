<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataData"
    data-layer="Data_1"
    data-type="Data"
    v-tooltip:right="'Data'"
    v-tooltipTutorial ="{text: activeAction.tooltip, actionStatus: activeAction.actionStatus}"
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
  },
  computed: {
    ...mapGetters({
      activeAction:  'mod_tutorials/getActiveAction',
    })
  }
}
</script>
