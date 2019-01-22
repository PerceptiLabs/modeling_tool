<template lang="pug">
  div.page(ref="layersbar")
    the-workspace
    the-toolbar
    the-layersbar
    the-sidebar
    the-info-popup(
      v-if="infoText"
      :infoText="infoText"
    )
</template>

<script src="./quantum.js"></script>

<style lang="scss">
  @import "../../scss/base";
  .page {
    display: grid;
    height: calc(100vh - #{$h-header});
    margin: 0;
    background-color: $bg-window;
    grid-template-areas:  'toolbar   toolbar    sidebar'
                          'layersbar  workspace sidebar';
    grid-template-rows: auto 1fr;
    grid-template-columns: auto 1fr auto;
  }
  .page_workspace {
    display: flex;
    overflow: hidden;
    flex-direction: column;

    grid-area: workspace;
  }
</style>
