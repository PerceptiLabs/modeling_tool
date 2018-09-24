<template lang="pug">
  div.page(ref="layersbar")
    the-workspace
    the-toolbar
    the-layersbar
    the-sidebar


</template>

<script>
  import TheToolbar from '@/components/the-toolbar.vue'
  import TheLayersbar from '@/components/the-layersbar.vue'
  import TheSidebar from '@/components/the-sidebar.vue'
  import TheWorkspace from '@/components/workspace/the-workspace.vue'

  export default {
    name: 'pageQuantum',
    components: {
      TheToolbar,
      TheLayersbar,
      TheSidebar,
      TheWorkspace
    },
    mounted() {
      var dragged;
      this.$refs.layersbar.addEventListener("dragstart", ( event )=> {
        if ( event.target.draggable) {
          // console.log(event)
          // console.log('dragstart')
          dragged = event.target;
          this.$store.commit('mod_workspace/ADD_dragElement', event)
          //make it half transparent
          event.target.style.opacity = .75;
        }
      }, false);

      this.$refs.layersbar.addEventListener("dragend", function( event ) {
        // reset the transparency
        //if ( event.target.className == "js-layersbar-draggable" ) {
          //console.log('dragend')
          //console.log(event)
          event.target.style.opacity = "";
        //}
      }, false);

      /* events fired on the drop targets */
      this.$refs.layersbar.addEventListener("dragover", function( event ) {
          event.preventDefault();
      }, false);

      this.$refs.layersbar.addEventListener("dragenter", function( event ) {
        if ( event.target.className.includes('network-field') ) {
          //event.target.style.cursor = "auto";
          //console.log('dragenter')
        }

      }, false);

      this.$refs.layersbar.addEventListener("dragleave", function( event ) {
        if ( event.target.className.includes('network-field')) {
          //console.log('dragleave')
          //event.target.style.cursor = "not-allowed";
        }
      }, false);

      this.$refs.layersbar.addEventListener("drop", ( event )=> {
        event.preventDefault();
        if ( event.target.className.includes('network-field') ) {
          this.$store.commit('mod_workspace/ADD_elToWorkspace', event)
        }
      }, false);
    },
  }
</script>

<style lang="scss">
  @import "../../scss/base";
  //@import "app";
  .page {
    background-color: $bg-window;
    display: grid;
    grid-template-areas:
            "toolbar toolbar sidebar"
            "layersbar workspace sidebar";
    grid-template-rows: auto 1fr;
    grid-template-columns: auto 1fr auto;
    height: 100vh;
    margin: 0;
  }
  .page_workspace {
    grid-area: workspace;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
</style>
