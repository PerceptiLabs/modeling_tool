<template lang="pug">
  aside.page_toolbar
    .toggle-wrap(:class="{'hide-layers': !hideLayers}")
      button.btn.btn--toolbar(type="button" @click="toggleLayers()")
        i.icon.icon-hide-top

    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-select
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-arrow-left

    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-step-prev
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-step-next
    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-on-off
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-pause
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-next
    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-repeat
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-box
    .settings-wrap
      button.btn.btn--settings(type="button") View settings

</template>

<script>
  export default {
    name: 'TheToolbar',
    computed: {
      hideLayers () {
        return this.$store.state.globalView.hideLayers
      }
    },
    methods: {
      toggleLayers () {
        this.$store.commit('globalView/SET_hideLayers', !this.hideLayers)
      }
    }
  }
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .page_toolbar {
    grid-area: toolbar;
    background-color: $bg-toolbar;
    display: flex;
    align-items: center;
    padding: 5px .5em 5px 0;
    height: $h-toolbar;
    //font-size: 11px;
  }
  .toggle-wrap {
    width: $w-layersbar;
    text-align: center;
    .btn--toolbar {
      @include multi-transition(transform);
      transform: rotate(0);
    }
    &.hide-layers {
      .btn--toolbar {
        transform: rotateX(-180deg);
      }
    }
  }
  .toolbar_list {
    padding: 0 .7143rem;
    margin: 0;
    list-style: none;
    display: flex;
    align-items: center;
    border-left: 1px solid $toolbar-border;
    li + li {
      margin-left: .3571rem;
    }
  }
  .settings-wrap {
    margin-left: auto;
  }
</style>
