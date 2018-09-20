<template lang="pug">
  div.page(ref="layersbar")
    main.page_workspace
      workspace-tabset
      workspace-content
    the-toolbar
    the-layersbar
    the-sidebar


</template>

<script>
  import TheToolbar from '@/components/the-toolbar.vue'
  import TheLayersbar from '@/components/the-layersbar.vue'
  import TheSidebar from '@/components/the-sidebar.vue'
  import WorkspaceContent from '@/components/workspace/workspace.vue'
  import WorkspaceTabset from '@/components/workspace/workspace-tabset.vue'

  export default {
    name: 'pageQuantum',
    components: {
      TheToolbar,
      TheLayersbar,
      TheSidebar,
      WorkspaceContent,
      WorkspaceTabset
    },
    mounted() {
      var dragged;
      //console.log(this.$refs.layersbar)
      this.$refs.layersbar.addEventListener("dragstart", function( event ) {
        // store a ref. on the dragged elem
        console.log(event)
        dragged = event.target;
        //make it half transparent
        event.target.style.opacity = .5;
      }, false);

      this.$refs.layersbar.addEventListener("dragend", function( event ) {
        // reset the transparency
        console.log('dragend')
        console.log(event)
        event.target.style.opacity = "";
      }, false);

      /* events fired on the drop targets */
      this.$refs.layersbar.addEventListener("dragover", function( event ) {
        // prevent default to allow drop
        console.log('dragover')
        event.preventDefault();
      }, false);

      this.$refs.layersbar.addEventListener("dragenter", function( event ) {
        // highlight potential drop target when the draggable element enters it
        console.log('dragenter')
        //if ( event.target.className == "vb-content" ) {
        event.target.style.background = "purple";
        //}

      }, false);

      this.$refs.layersbar.addEventListener("dragleave", function( event ) {
        // reset background of potential drop target when the draggable element leaves it
        console.log('dragend')
        //if ( event.target.className == "vb-content" ) {
        event.target.style.background = "";
        //}

      }, false);

      this.$refs.layersbar.addEventListener("drop", function( event ) {
        // prevent default action (open as link for some elements)
        console.log('drop')
        console.log(event)
        event.preventDefault();
        // move dragged elem to the selected drop target
        //if ( event.target.className == "vb-content" ) {
        event.target.style.background = "";
        var styles = `position: absolute; top: ${(event.offsetY - 35)}px; left: ${(event.offsetX - 35)}px;`
        const copy = dragged.cloneNode(true);
        copy.style.cssText = styles;
        event.target.appendChild(copy);
        //}

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
