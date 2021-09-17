<template lang="pug">
  header(
    v-if="showIfTypeIs(['image', 'numerical', 'mask'])"
    :class="{'is-open': selectedIndex === index}"
  )
    div.svg-wrapper(@click="toggle()")
      svg(width="12" height="9" viewBox="0 0 12 9" fill="none" xmlns="http://www.w3.org/2000/svg")
        path(fill-rule="evenodd" clip-rule="evenodd" d="M0.5 8.5C0.5 8.36739 0.552679 8.24021 0.646447 8.14645C0.740215 8.05268 0.867392 8 1 8H5C5.13261 8 5.25979 8.05268 5.35355 8.14645C5.44732 8.24021 5.5 8.36739 5.5 8.5C5.5 8.63261 5.44732 8.75979 5.35355 8.85355C5.25979 8.94732 5.13261 9 5 9H1C0.867392 9 0.740215 8.94732 0.646447 8.85355C0.552679 8.75979 0.5 8.63261 0.5 8.5ZM0.5 4.5C0.5 4.36739 0.552679 4.24021 0.646447 4.14645C0.740215 4.05268 0.867392 4 1 4H8C8.13261 4 8.25979 4.05268 8.35355 4.14645C8.44732 4.24021 8.5 4.36739 8.5 4.5C8.5 4.63261 8.44732 4.75979 8.35355 4.85355C8.25979 4.94732 8.13261 5 8 5H1C0.867392 5 0.740215 4.94732 0.646447 4.85355C0.552679 4.75979 0.5 4.63261 0.5 4.5ZM0.5 0.5C0.5 0.367392 0.552679 0.240215 0.646447 0.146447C0.740215 0.0526785 0.867392 0 1 0H11C11.1326 0 11.2598 0.0526785 11.3536 0.146447C11.4473 0.240215 11.5 0.367392 11.5 0.5C11.5 0.632608 11.4473 0.759785 11.3536 0.853553C11.2598 0.947321 11.1326 1 11 1H1C0.867392 1 0.740215 0.947321 0.646447 0.853553C0.552679 0.759785 0.5 0.632608 0.5 0.5Z" fill="white")
  div(v-else) &nbsp;   
</template>
<script>
import { mapGetters } from 'vuex';
export default {
  name: "DataColumnOptions",
  props:{
    index: {
      type: Number,
      default: null,
    },
    columnSelectedType: {
      type: Array,
      default: [],
    }
  },
  data() {
    return {
    }
  },
  computed: {
    dataTypeSelected() {
      return this.columnSelectedType[this.index];
    },
    ...mapGetters({
      selectedIndex: 'mod_dataWizardPreprocessing/getElementPreProcessingIndex',
    })
    
  },
  methods: {
    toggle(){
      if(this.selectedIndex === this.index) {
        this.$store.dispatch('mod_dataWizardPreprocessing/TOGGLE_elementPreProcessing', null);
      } else if(this.selectedIndex === null) {
        this.$store.dispatch('mod_dataWizardPreprocessing/TOGGLE_elementPreProcessing', this.index);
      }
    },
    showIfTypeIs(arrOfAllowedTypes = []) {
      return arrOfAllowedTypes.some(el => el === this.dataTypeSelected);
    }
  }
}
</script>
<style lang="scss" scoped>
header {
  &.is-open {
    .svg-wrapper {
      background-color: #131B30;
    }
  }
}
.svg-wrapper {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 25px;
  height: 25px;
  padding: 2px 5px;
  border-radius: 2px;
  transition: 0.3s;
  &:hover {
    background-color: #131B30;
  }
}
</style>
