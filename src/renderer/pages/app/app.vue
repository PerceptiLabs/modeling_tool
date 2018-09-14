<template lang="pug">
  div.page
    main.page_workspace
      p Network_1
    the-toolbar
    the-layersbar
    aside.page_sidebar
      p Project  Save  Import  Code
      h4 Layers


</template>

<script>
  import TheToolbar from '@/components/the-toolbar.vue'
  import TheLayersbar from '@/components/the-layersbar.vue'

  export default {
    name: 'pageApp',
    components: {
      TheToolbar,
      TheLayersbar
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
    grid-template-columns: $w-layersbar 1fr 300px;
    min-height: 100vh;
    margin: 0;
  }
  .page_workspace {
    grid-area: workspace;
    background-color: #23252A;
    padding: 20px;
  }


  .page_sidebar {
    grid-area: sidebar;
    padding: 20px;
    //background-color: #ff0;
  }
</style>
