<template lang="pug">
  transition(name="scroll-right")
    aside.page_sidebar(v-show="hideSidebar")
      p Project  Save  Import  Code
      h4 Layers
</template>

<script>
export default {
  name: 'TheSidebar',
  computed: {
    hideSidebar () {
      return this.$store.state.globalView.hideSidebar
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .page_sidebar {
    grid-area: sidebar;
    max-width: 300px;
    overflow: hidden;
  }
  //Animations
  .scroll-right-enter-active, .scroll-right-leave-active {
    transition: max-width .5s;
  }
  .scroll-right-enter, .scroll-right-leave-to {
    max-width: 0;
  }
</style>
