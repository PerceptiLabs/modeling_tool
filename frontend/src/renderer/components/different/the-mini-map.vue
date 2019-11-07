<template lang="pug">
  .mini-map-wrap
    base-checkbox.mini-map-wrap_toggle(
      :icon-theme="true"
      v-model="isShowMap") Map
    .mini-map(v-if="isShowMap")
      .mini-map_head
        button.btn.btn--link.icon.icon-close(type="button"
          @click="closeMap"
          )
      .mini-map_main
        network-field.mini-map_canvas(
          :style="canvasStyle"

        )

</template>

<script>
  import NetworkField           from '@/components/network-field/network-field.vue'
export default {
  name: "TheMiniMap",
  components: {NetworkField},
  mounted() {
  },
  data() {
    return {
      isShowMap: false
    }
  },
  computed: {
    currentNetList() {
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
    },
    canvasSize() {
      return this.$store.state.mod_workspaceHelpers.networkSize
    },
    canvasStyle() {
      //30/20
      const size = this.canvasSize;
      console.log(size);
      const width = 300 / size.width;
      const height = 200 / size.height;
      const scale = (width > height) ? height : width;
      console.log(scale);
      return {
        width: size.width+'px',
        height: size.height+'px',
        transform: `scale(${scale})`
      }
    }
  },
  watch: {
    currentNetList: {
      handler() {
        if(this.isShowMap) this.updateMiniMap()
      },
      deep: true
    },
    isShowMap(newVal) {
      if(newVal) this.$nextTick(()=> this.updateMiniMap())
      //if(newVal) setTimeout(()=> {this.updateMiniMap()}, 1000)
    }
  },
  methods: {
    closeMap() {
      this.isShowMap = false
    },
    updateMiniMap() {

    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .mini-map-wrap {
  }
  .mini-map-wrap_toggle {

  }
  .mini-map {
    position: absolute;
    bottom: 130%;
    left: 10px;
    width: 30rem;
    height: 20rem;
    overflow: hidden;
    border: 1px solid #383F50;
    z-index: 1000;
  }
  .mini-map_head {
    padding: .5rem;
    background-color: #383F50;
  }
  .mini-map_main {
    //background-color: #23252A;
    background-color: #555;
  }
  .mini-map_canvas {
    //background-color: #555;
    transform-origin: top left;
    transform: scale(0.25);
    //transform: matrix(0.0820513, 0, 0, 0.0820513, -1790.5, -752.5);
  }
</style>
