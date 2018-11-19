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
    background-color: $bg-window;
    display: grid;
    grid-template-areas:
      "toolbar    toolbar   sidebar"
      "layersbar  workspace sidebar";
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
