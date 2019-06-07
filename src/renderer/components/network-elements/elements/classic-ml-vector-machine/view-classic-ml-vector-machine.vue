<template lang="pug">
  .btn.btn--layersbar.net-element-learn-class(:draggable="draggable"
    data-component="ClassicMLSVM"
    data-layer="Support Vector Machine"
    data-type="Training"
    v-tooltip:right="'Support Vector Machine'"
    v-tooltip-interactive:right="interactiveInfo.MLSvm"
  )
    i.icon.icon-round-figur2

</template>

<script>
export default {
  name: 'ViewClassicMLSVM',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      interactiveInfo: {
        MLSvm: {
          title: 'MLSvm',
          text: 'SVM layer'
        }
      }
    }
  }
}
</script>
