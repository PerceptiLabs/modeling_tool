<template lang="pug">
  .net-element.clickout(
    ref="rootBaseElement"
    :style="style"
    :class="active ? 'active' : 'inactive'"
    @dblclick.stop.prevent="layerContainer ? $emit('dblcl') : openSettings()"
    @contextmenu.stop.prevent="openContext"
    )
    //@mousedown="bodyDown($event)"
    .net-element_btn
      slot

    .net-element_window(v-if="settingsIsOpen ")
      slot(name="settings")

    .net-element_window.net-element_context-menu(v-if="contextIsOpen")
      slot(name="context")

</template>

<script>
import baseNetDrag        from '@/core/mixins/base-net-drag.js';
import baseNetFunctional  from '@/core/mixins/base-net-functional.js';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
import clickOutside       from '@/core/mixins/click-outside.js'

export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetFunctional, baseNetPaintArrows, clickOutside],
  props: {
    layerContainer: {type: Boolean, default: false},
  },
  data() {
      return {

      }
  },
  methods: {
    clickOutsideAction() {
      this.deselect()
    }
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
    .active & .btn{
      box-shadow: 0 0 20px #fff;
    }
  }
</style>
