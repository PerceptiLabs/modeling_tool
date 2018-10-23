<template lang="pug">
  .net-element(
    ref="rootBaseElement"
    :style="style"
    :class="active ? 'active' : 'inactive'"
    @dblclick.stop.prevent="openSettings"
    @contextmenu.stop.prevent="openContext"
    )
    //@mousedown="bodyDown($event)"
    button.net-element_btn(type="button"
      ref="btn"
      @blur="blurElement"
      )
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
export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetFunctional, baseNetPaintArrows],
  props: {
    layerClass: {type: String, default: ''},
    iconClass:  {type: String, default: ''},
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
    .active & .btn{
      box-shadow: 0 0 20px #fff;
    }
  }
</style>
