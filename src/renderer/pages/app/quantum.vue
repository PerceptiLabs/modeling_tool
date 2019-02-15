<template lang="pug">
  .page(ref="layersbar" v-if="showPage")
    the-workspace
    the-toolbar
    the-layersbar
    the-sidebar
    the-info-popup(
      v-if="infoText"
      :infoText="infoText"
    )
    the-tutorial
</template>

<script src="./quantum.js"></script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .page {
    display: grid;
    background-color: $bg-window;
    grid-template-areas:  'toolbar   toolbar    sidebar'
                          'layersbar  workspace sidebar';
    grid-template-rows: auto 1fr;
    grid-template-columns: auto 1fr auto;
  }
</style>
