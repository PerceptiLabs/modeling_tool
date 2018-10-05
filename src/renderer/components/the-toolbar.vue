<template lang="pug">
  aside.page_toolbar
    div
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

    .test-api
      span.big-text Dev Mode:
        span.text-error  {{ devMode }}
      span.big-text Version:
        span.text-error  {{ versionApi }}
      input.text-error.big-text(v-model="x")
      span.big-text +
      input.text-error.big-text(v-model="y")
      button.btn.btn--settings(type="button" @click="calcPY") Calc
      span.big-text =
      span.big-text {{ resultSym }}

</template>

<script>
  import configApp from '@/core/globalSettings.js'
  export default {
    name: 'TheToolbar',
    data() {
      return {
        x: null,
        y: null,
      }
    },
    computed: {
      hideLayers () {
        return this.$store.state.globalView.hideLayers
      },
      resultSym() {
        return this.$store.state.mod_api.symPY
      },
      versionApi() {
        return configApp.version
      },
      devMode() {
        return configApp.developMode
      }
    },
    methods: {
      toggleLayers () {
        this.$store.commit('globalView/SET_hideLayers', !this.hideLayers)
      },
      PY() {
        this.$store.dispatch('mod_pythonAPI/PY_console');
      },
      calcPY() {
        let x = +this.x;
        let y = +this.y;
        //this.$store.dispatch('mod_pythonAPI/PY_text', {x, y});
        this.$store.dispatch('mod_api/PY_func', {x, y});
      }
    }
  }
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .page_toolbar {
    grid-area: toolbar;
    background-color: $bg-toolbar;

    padding: 5px .5em 5px 0;
    //height: $h-toolbar;
    //font-size: 11px;
    > div {
      display: flex;
      align-items: center;
    }
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
  .test-api {
    display: flex;
    align-items: center;
    font-weight: bold;
    > * {
      margin: 0 .5em;
    }
    input {
      width: 5em;
    }
    span span {
      font-weight: normal;
    }
  }
</style>
