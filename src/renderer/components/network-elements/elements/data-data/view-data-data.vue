<template lang="pug">
  .btn.btn--layersbar.net-element-data(:draggable="draggable"
    data-component="DataData"
    data-layer="Data_1"
    data-type="Data"
    v-tooltip:right="'Data'"
    v-tooltipTutorial ="{text: activeAction.tooltip, actionName: tutorialActionName('two'), test: 'from data data'}"
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
  },
  methods: {
    tutorialActionName(value) {
      return this.activeAction.name === value
    }
  }
}
</script>
