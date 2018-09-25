import IoInput from '@/components/network-elements/io-input.vue'
import IoOutput from '@/components/network-elements/io-output.vue'
//import DataData from '@/components/network-elements/io-output.vue'
//import IoOutput from '@/components/network-elements/io-output.vue'

export default {
  name: 'WorkspaceContent',
  components: {
    //DragR,
    IoInput,
    IoOutput
    //BaseNetElement
  },
  data () {
    return {
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
