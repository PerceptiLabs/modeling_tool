<template lang="pug">
  transition(name="scroll-left")
    aside.page_layersbar(v-show="hideLayers")
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
  name: 'TheLayersbar',
  computed: {
    hideLayers () {
      return this.$store.state.globalView.hideLayers
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .page_layersbar {
    grid-area: layersbar;
    overflow: hidden;
    max-width: $w-layersbar;
  }
  .layersbar-list {
    padding: 0;
    margin: 0;
    list-style: none;
    transform: translateY(0);
    transition: transform $animation-speed $animation-speed;
    > li {
      padding: 5px;
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

  //Animations
  .scroll-left-enter {
    max-width: 0;
    .layersbar-list {
      transform: translateY(-120%);
    }
  }
  .scroll-left-enter-active {
    transition: max-width $animation-speed 0s;
  }
  .scroll-left-leave-active {
    transition: max-width $animation-speed $animation-speed;
    .layersbar-list {
      transition: transform $animation-speed;
    }
  }
  .scroll-left-leave-to {
    max-width: 0;
    .layersbar-list {
      transform: translateY(-120%);
    }
  }

</style>
