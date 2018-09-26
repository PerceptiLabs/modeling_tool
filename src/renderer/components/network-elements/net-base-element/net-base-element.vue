<template lang="pug">
  .net-element(
    :style="style"
    :class="active || isActive ? 'active' : 'inactive'"
    @mousedown.stop.prevent="bodyDown($event)"
    @touchstart.stop.prevent="bodyDown($event)"
    @dblclick="openSettings"
    @contextmenu="openContext"
    )
    //@mousedown="bodyDown($event)"
    button.net-element_btn(type="button"
      ref="btn"
      @blur="blurElement"
      )
      slot

    .net-element_window(v-if="settingsIsOpen")
      slot(name="settings")

    .net-element_window.net-element_context-menu(v-if="contextIsOpen")
      slot(name="context")

</template>

<script>
import baseNetDrag        from '@/core/mixins/base-net-drag.js';
import baseNetFunctional  from '@/core/mixins/base-net-functional.js';
export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetFunctional],
  inject: ['dataEl'],
  props: {
    layerClass: {type: String, default: ''},
    iconClass: {type: String, default: ''},
    //dataEl: {type: Object}
  },
  data() {
      return {

      }
  },
  methods: {

  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  .net-element_window {
    position: absolute;
    z-index: 2;
    left: 100%;
    top: 0;
    padding-left: 10px;
  }
  .net-element_btn {
    padding: 0;
    margin: 0;
    background-color: transparent;
  }
</style>
