<template lang="pug">
  main.page_workspace
    .workspace_tabset
      include workspace-tabset.pug
    .workspace
      .workspace_content(v-bar)
        div
          .network-field(
            v-for="(net, i) in workspace"
            :key="i"
            v-if="currentNetwork == i"
            :style="'transform: scale(' + styleScale + ')'"
            )
            drag-r(
              v-for="(c, i) in net.network"
              :key="i"
              :id="c.layerId"
              :isResizable="false"
              :isDraggable="c.meta.isDraggable"
              :x="c.meta.left"
              :y="c.meta.top"
              @dragstop="resize($event, i)"
              @clicked="onActivated")
              component(:is="c.componentName")

            //component(
              v-for="(c, i) in network"
              //:key="i"
              //:is="c.componentName"
              )

      .workspace_meta
        .workspace_scale
          button.btn.btn--icon(type="button" @click="decScale()") -

          .scale-input
            input(type="text" v-model.number="scale")
            span %

          button.btn.btn--icon(type="button" @click="incScale()") +

          base-checkbox Map



</template>

<script>
//import VueDrag from 'vue-drag-resize'
import IoInput from '@/components/network-elements/io-input.vue'
import IoInputs from '@/components/network-elements/layer-io.vue'
import DragR from '@/components/base/drag/vue-drag-resize.vue'

export default {
  name: 'WorkspaceContent',
  components: {
    DragR,
    IoInput,
    IoInputs
  },
  data () {
    return {
      network: [
        {
          layerId: 1,
          layerName: 'Layer Name',
          layerChild: [2,3,5],
          componentName: 'io-input',
          meta: {
            isVisible: true,
            isDraggable: true,
            top: 50,
            left: 50
          }
        }
      ],
      scale: 100
    }
  },
  computed: {
    styleScale() {
      return this.scale / 100
    },
    workspace() {
      return this.$store.state.mod_workspace.workspaceContent
    },
    currentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
    hideSidebar () {
      return this.$store.state.globalView.hideSidebar
    },
  },
  methods: {
    // addLayer(e) {
    //   console.log('addLayer')
    //   let layer = {
    //     layerId: e.timeStamp,
    //     layerName: e.target.dataset.layer,
    //     layerChild: null,
    //     componentName: e.target.dataset.component,
    //     meta: {
    //       isVisible: true,
    //       isDraggable: true,
    //       top: e.offsetY - e.target.clientHeight/2,
    //       left: e.offsetX - e.target.clientWidth/2
    //     }
    //   }
    //   this.network.push(layer);
    // },

    toggleSidebar () {
      this.$store.commit('globalView/SET_hideSidebar', !this.hideSidebar)
    },
    decScale () {
      if (this.scale < 10) {
        this.scale = 5
      }
      else this.scale = this.scale - 10
    },
    incScale () {
      if (this.scale > 90) {
        this.scale = 100
      }
      else this.scale = this.scale + 10
    },
    resize(newRect, i) {
      //console.log(newRect);
      //console.log(i);
      // this.network[i].meta.top = newRect.top;
      // this.network[i].meta.left = newRect.left;
    },
    onActivated(e) {
      //console.log(e)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  @import "./workspace-tabset";
  .workspace {
    display: flex;
    flex-direction: column;
    flex: 1 1 100%;
  }
  .workspace_tabset {
    padding-top: 2px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .workspace_content {
    background-color: $bg-workspace;
    flex: 1 1 100%;
    overflow: scroll;
  }
  .workspace_meta {
    flex: 0 0 auto;
    background-color: $bg-workspace-2;
    display: flex;
    justify-content: space-between;
  }
  .workspace_scale {
    display: flex;
    align-items: center;
  }
  .scale-input {
    position: relative;
    input {
      padding-right: 1em;
      width: 50px;
    }
    span {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      right: .5em;

    }
  }
  .network-field {
    height: 100%;
  }
</style>
