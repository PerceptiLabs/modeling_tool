<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabSet"
        :key="tab.i"
        :class="{'disable': tabSelected != i}"
        @click="setTab(i)"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body.active(
        v-for="(tabContent, i) in tabSet"
        :key="tabContent.i"
        v-if="tabSelected === i"
        )
        .settings-layer
          slot(:name="tabContent+'-content'")
        .settings-layer_foot
          slot(name="action")

</template>

<script>
export default {
  name: 'NetBaseSettings',
  props: {
    tabSet: {
      type: Array,
      default: function() {
        return ['Settings', 'Code']
      }
    }
  },
  data() {
    return {
      tabSelected: 0,
    }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i;
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  .popup {
    min-width: 29rem;
    box-shadow: $layer-shad;
  }
  .popup_body {
    max-width: calc(50vw - #{$w-sidebar});
    min-width: 29rem;
    overflow: hidden;
  }
  .popup_body--show-code {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    top: 0;
    max-width: none;
    background-color: $bg-toolbar;
  }
  .settings-layer {
    max-height: calc(100vh - 26rem);
    overflow: auto;
  }
</style>
