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
        canvas.mini-map_canvas(
          ref="miniMapCanvas"
        )

</template>

<script>
  import '@/core/plugins/mini-map.js'
export default {
  name: "TheMiniMap",
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
      pagemap(this.$refs.miniMapCanvas, {
        viewport: document.querySelector('#minimap'),
        interval: null,
        styles: { div: 'rgba(0,0,0,0.2)' },
        //back: 'rgba(255,255,255,1)'
        view: 'rgba(255,255,255,0.1)',
        drag: 'rgba(255,255,255,0.2)',
      });
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .mini-map-wrap {
    //position: relative;
  }
  .mini-map-wrap_toggle {

  }
  .mini-map {
    position: absolute;
    bottom: 130%;
    left: 10px;
    //width: 25rem;
    //height: 15rem;
    border: 1px solid #383F50;
    z-index: 1000;
  }
  .mini-map_head {
    padding: .5rem;
    background-color: #383F50;
  }
  .mini-map_main {
    background-color: #23252A;
  }
  .mini-map_canvas {
    vertical-align: middle;
  }
</style>
