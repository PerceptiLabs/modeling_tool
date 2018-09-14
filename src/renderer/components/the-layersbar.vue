<template lang="pug">
  aside.page_layersbar
    ul.layersbar-list
      li
        button.btn.btn--layersbar
          i.icon.icon-data-toggle
      li
        button.btn.btn--layersbar
          i.icon.icon-data
      li
        button.btn.btn--layersbar
          i.icon.icon-data
      li
        button.btn.btn--layersbar
          i.icon.icon-settings
      li
        button.btn.btn--layersbar
          i.icon.icon-network
      li
        button.btn.btn--layersbar
          i.icon.icon-mind
      li
        button.btn.btn--layersbar
          i.icon.icon-calc
      li
        button.btn.btn--layersbar
          i.icon.icon-add

</template>

<script>
export default {
  name: 'TheLayersbar'
}
</script>

<style lang="scss" scoped>
  .page_layersbar {
    grid-area: layersbar;
    padding: 5px;
  }
  .layersbar-list {
    padding: 0;
    margin: 0;
    list-style: none;
    > li {
      + li {
        margin-top: 10px;
      }
      &:nth-child(1n) button {
        background: linear-gradient(#D3DFFE, #A1A9BF  );
      }
      &:nth-child(2n) button {
        background: linear-gradient(#4C63A6, #384E8E   );
      }
      &:nth-child(3n) button {
        background: linear-gradient(#73FEBB, #61E6EE   );
      }
      &:nth-child(4n) button {
        background: linear-gradient(#FECF73, #EEB661   );
      }
      &:nth-child(5n) button {
        background: linear-gradient(#FE7373, #EE6161   );
      }
      &:nth-child(6n) button {
        background: linear-gradient(#E273FE, #B061EE   );
      }
      &:nth-child(7n) button {
        background: linear-gradient(#7389FE, #6167EE   );
      }
    }
  }
</style>
