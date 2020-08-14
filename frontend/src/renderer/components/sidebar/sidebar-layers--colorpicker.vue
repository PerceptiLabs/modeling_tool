<template lang="pug">
  .layer-colorpicker.js-clickout
    //- button.btn.btn--icon.layer-item--btn-action(type="button"
    //-   :class="layerItemColor"
    //-   :style="iconColor"
    //-   @click="toggleColorpicker($event)"
    //-   )
      //- i.icon.icon-ellipse
      //- .layer-item-color-block
    .layer-item-color-block(type="button"
      :class="layerItemColor"
      :style="iconColor"
      @click="toggleColorpicker($event)"
      )
    .layer-colorpicker_wrap(v-if="showColorpicker")
      .form_row
        base-checkbox(v-model="applyColor")
        input(type="text" v-model="layerColor.hex")
      color-picker(v-model="layerColor")

</template>

<script>
  import { Slider } from 'vue-color'
  import clickOutside       from '@/core/mixins/click-outside.js'
  import { layerBgColor }       from '@/core/helpers.js'
  
export default {
  name: 'SidebarLayersColorPicker',
  mixins: [clickOutside],
  components: {
    'color-picker': Slider
  },
  props: {
    currentLayer: {
      type: Object,
      default: function () {
        return null
      }
    },
  },
  data() {
    return {
      showColorpicker: false,
      applyColor: false,
      layerColor: {
        a:1,
        hex:"#BF4040",
        hex8:"#BF4040FF",
        hsl: {a:1,h:0,l:0.5,s:0.5},
        hsv: {a:1,h:0,s:0.6666666666666666,v:0.75},
        oldHue:2.4324324324324342,
        rgba: {a:1,b:64,g:64,r:191},
        source:"hsl"
      },
    }
  },
  computed: {
    iconColor() {
      return this.applyColor
        ? {'background-color': this.layerColor.hex}
        : ''
    },
    layerItemColor() {
      return layerBgColor(this.currentLayer.componentName)
    },
  },
  watch: {
    iconColor(newVal) {
      const color = newVal ? newVal.color : '';
      this.$store.commit('mod_workspace/SET_elementBgColor', {id: this.currentLayer.layerId, color})
    }
  },
  methods: {
    clickOutsideAction() {
      this.showColorpicker = false
    },
    toggleColorpicker(ev) {
      if(this.showColorpicker) {
        this.showColorpicker = false;
        document.removeEventListener('click', this.clickOutside);
      }
      else {
        this.showColorpicker = true;
        this.ClickElementTracking = ev.target.closest('.js-clickout');
        document.addEventListener('click', this.clickOutside);
      }
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .layer-colorpicker {
    position: relative;
  }
  .layer-colorpicker_wrap {
    background: rgba($bg-workspace, .9);
    padding: 1rem;
    box-shadow: $icon-shad;
    position: absolute;
    z-index: 2;
    top: 100%;
  }
  .layer-item-color-block {
    width: 8px;
    height: 8px;
    border-radius: 2px;
  }
</style>
