<template lang="pug">
  .layer-colorpicker
    button.btn.btn--icon.layer-item--btn-action(type="button"
      :class="layerItemColor"
      :style="iconColor"
      @click="toggleColorpicker"
      )
      i.icon.icon-ellipse
    .layer-colorpicker_wrap(v-if="showColorpicker")
      .form_row
        base-checkbox(v-model="applyColor")
        input(type="text" v-model="layerColor.hex")
      color-picker(v-model="layerColor")

</template>

<script>
  import { Slider } from 'vue-color'
  import clickOutside       from '@/core/mixins/click-outside.js'

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
        ? {'color': this.layerColor.hex}
        : ''
    },
    layerItemColor() {
      let className = '';
      switch (this.currentLayer.componentName) {
        case 'DataData':
        case 'DataEnvironment':
          className = 'net-color-data';
          break;
        case 'DeepLearningFC':
        case 'DeepLearningConv':
        case 'DeepLearningDeconv':
        case 'DeepLearningRecurrent':
          className = 'net-color-learn-deep';
          break;
        case 'ProcessCrop':
        case 'ProcessEmbed':
        case 'ProcessGrayscale':
        case 'ProcessOneHot':
        case 'ProcessReshape':
          className = 'net-color-process';
          break;
        case 'TrainNormal':
        case 'TrainGenetic':
        case 'TrainDynamic':
        case 'TrainReinforce':
          className = 'net-color-train';
          break;
        case 'MathArgmax':
        case 'MathMerge':
        case 'MathSplit':
        case 'MathSoftmax':
          className = 'net-color-math';
          break;
        case 'ClassicMLDbscans':
        case 'ClassicMLKMeans':
        case 'ClassicMLKNN':
        case 'ClassicMLRandomForest':
        case 'ClassicMLSVM':
          className = 'net-color-learn-class';
          break;
        case 'LayerContainer':
          className = 'net-color-layercontainer';
          break;
      }
      return [className];
    }
  },
  watch: {
    iconColor(newVal) {
      const color = newVal ? newVal.color : '';
      this.$store.commit('mod_workspace/SET_elementBgColor', {id: this.currentLayer.layerId, color})
    }
  },
  methods: {
    toggleColorpicker() {
      this.showColorpicker = !this.showColorpicker
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
</style>
