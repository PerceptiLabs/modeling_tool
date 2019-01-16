import fs from 'fs';
import {remote} from 'electron'
import {openLoadDialog} from '@/core/helpers.js'



import TheToolbar   from '@/components/the-toolbar.vue'
import TheLayersbar from '@/components/the-layersbar.vue'
import TheSidebar   from '@/components/the-sidebar.vue'
import TheWorkspace from '@/components/workspace/the-workspace.vue'
import TheInfoPopup from "@/components/global-popups/the-info-popup";

export default {
  name: 'pageQuantum',
  components: {
    TheToolbar,
    TheLayersbar,
    TheSidebar,
    TheWorkspace,
    TheInfoPopup
  },
  beforeCreate() {
    this.$store.commit('mod_workspace/ADD_network');
  },
  created() {
    this.$store.dispatch('mod_api/API_runServer');
  },
  mounted() {
    this.addDragListener();
  },
  data() {
    return {
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
    eventLoadNetwork() {
      return this.$store.state.mod_events.openNetwork
    },
    eventSaveNetwork() {
      return this.$store.state.mod_events.saveNetwork
    },
    currentNetwork() {
      return this.$store.getters['mod_workspace/GET_currentNetwork']
    },
    networkMode() {
      return this.currentNetwork.networkMeta.netMode
    },
  },

  watch: {
    eventLoadNetwork() {
      let opt = {
        title:"Load Network",
        filters: [
          {name: 'Text', extensions: ['json']},
        ]
      };
      this.openLoadDialog(this.loadNetwork, opt)
    },
    eventSaveNetwork() {
      this.saveNetwork()
    },
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
    }
  },
  methods: {
    openLoadDialog,
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

    loadNetwork(pathArr) {
      fs.readFile(pathArr[0],
        (err, data)=> {
        if(data) {
          let net = JSON.parse(data.toString());
          this.$store.commit('mod_workspace/ADD_network', net)
        }
        else {
          console.error(err);
        }
      });
    },
    saveNetwork() {
      const dialog = remote.dialog;
      const network = this.currentNetwork;
      const jsonNet = cloneNet(network);

      const option = {
        title:"Save Network",
        defaultPath: `*/${network.networkName}`,
        filters: [
          {name: 'Text', extensions: ['json']},
        ]
      };

      dialog.showSaveDialog(null, option, (fileName) => {
        if (fileName === undefined){
          console.log("You didn't save the file");
          return;
        }
        fs.writeFile(fileName, jsonNet, (err) => {
          if(err){
            alert("An error ocurred creating the file "+ err.message)
          }

          alert("The file has been succesfully saved");
        });
      });
      function cloneNet(net) {
        var outNet = {};
        for (var key in net) {
          if(key === 'network') {
            outNet[key] = JSON.parse(cloneEl(net[key]))
          }
          else {
            outNet[key] = net[key];
          }
        }
        outNet.networkMeta = {};
        return JSON.stringify(outNet, null, ' ');
      }
      function cloneEl(el) {
        return JSON.stringify(el, (key, val)=> {
          if (key === 'calcAnchor') {
            return undefined;
          }
          return val;
        }, ' ');
      }
    },
  }
}
