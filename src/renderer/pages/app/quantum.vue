<template lang="pug">
  div.page
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
    }
  }
</script>

<style lang="scss" scoped>
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
    min-height: 100vh;
    margin: 0;
  }
  .page_workspace {
    grid-area: workspace;
    display: flex;
    flex-direction: column;
  }
</style>
