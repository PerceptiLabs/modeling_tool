import TheToolbar   from '@/components/the-toolbar.vue'
import TheLayersbar from '@/components/the-layersbar.vue'
import TheSidebar   from '@/components/the-sidebar.vue'
import TheWorkspace from '@/components/workspace/the-workspace.vue'
import TheInfoPopup from "@/components/global-popups/the-info-popup";
import TheTutorial  from "@/components/tutorial/the-tutorial";

export default {
  name: 'pageQuantum',
  components: {
    TheToolbar,
    TheLayersbar,
    TheSidebar,
    TheWorkspace,
    TheInfoPopup,
    TheTutorial
  },
  created() {
    if(this.currentNetwork[0] === "empty app") {
      this.$store.dispatch('mod_workspace/ADD_network', {'ctx': this});
    }
  },
  mounted() {
    this.showPage = true;
    this.$nextTick(()=> this.addDragListener())
  },
  data() {
    return {
      showPage: false,
      dragMeta: {
        dragged: null,
        //outClassName: 'network-field'
        outClassName: 'svg-arrow'
      }
    }
  },
  computed: {
    infoText() {
      return this.$store.state.globalView.globalPopup.showInfoPopup
    },
    currentNetwork() {
      return this.$store.getters['mod_workspace/GET_currentNetwork']
    },
    networkMode() {
      return this.currentNetwork.networkMeta
        ? this.currentNetwork.networkMeta.netMode
        : 'edit'
    },
  },
  watch: {
    networkMode(newVal) {
      if(newVal == 'edit') {
        this.$nextTick(function () {
          this.addDragListener()
        })
      }
      else {
        this.$refs.layersbar.removeEventListener("dragstart", this.dragStart, false);
        this.offDragListener();
      }
    },
    currentNetwork: {
      handler() {
        this.$store.dispatch('mod_api/API_getBeForEnd');
      },
      deep: true
    }
  },
  methods: {
    addDragListener() {
      this.$refs.layersbar.addEventListener("dragstart", this.dragStart, false);
    },
    offDragListener() {
      this.$refs.layersbar.removeEventListener("dragend", this.dragEnd, false);
      this.$refs.layersbar.removeEventListener("dragover", this.dragOver, false);
      this.$refs.layersbar.removeEventListener("dragenter", this.dragEnter, false);
      this.$refs.layersbar.removeEventListener("dragleave", this.dragLeave, false);
      this.$refs.layersbar.removeEventListener("drop", this.dragDrop, false);
    },
    dragStart(event) {
      if ( event.target.draggable && this.networkMode === 'edit' && event.target.className.includes('btn--layersbar')) {
        this.$refs.layersbar.addEventListener("dragend", this.dragEnd, false);
        this.$refs.layersbar.addEventListener("dragover", this.dragOver, false);
        this.$refs.layersbar.addEventListener("dragenter", this.dragEnter, false);
        this.$refs.layersbar.addEventListener("dragleave", this.dragLeave, false);
        this.$refs.layersbar.addEventListener("drop", this.dragDrop, false);

        this.dragMeta.dragged = event.target;
        this.$store.commit('mod_workspace/ADD_dragElement', event);
        event.target.style.opacity = .75;
      }
    },
    dragEnd(event) {
      this.offDragListener();
      event.target.style.opacity = "";
    },
    dragOver(event) {
      event.preventDefault();
    },
    dragEnter(event) {},
    dragLeave(event) {},
    dragDrop(event) {
      event.preventDefault();
      if ( event.target.classList[0] === this.dragMeta.outClassName) {
        this.$store.dispatch('mod_workspace/ADD_element', event)
      }
    },
  }
}
