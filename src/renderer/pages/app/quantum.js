import fs from 'fs';
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
  mounted() {
    let dragged;
    let outClassName = 'network-field';
    this.$refs.layersbar.addEventListener("dragstart", ( event )=> {
      if ( event.target.draggable) {
        // console.log(event)
        // console.log('dragstart')
        dragged = event.target;
        this.$store.commit('mod_workspace/ADD_dragElement', event)
        //make it half transparent
        event.target.style.opacity = .75;
      }
    }, false);

    this.$refs.layersbar.addEventListener("dragend", function( event ) {
      // reset the transparency
      //if ( event.target.className == "js-layersbar-draggable" ) {
      //console.log('dragend')
      //console.log(event)
      event.target.style.opacity = "";
      //}
    }, false);

    /* events fired on the drop targets */
    this.$refs.layersbar.addEventListener("dragover", function( event ) {
      event.preventDefault();
    }, false);

    this.$refs.layersbar.addEventListener("dragenter", function( event ) {
      if ( event.target.className.includes(outClassName) ) {
        //event.target.style.cursor = "auto";
        //console.log('dragenter')
      }

    }, false);

    this.$refs.layersbar.addEventListener("dragleave", function( event ) {
      if ( event.target.className.includes(outClassName)) {
        //console.log('dragleave')
        //event.target.style.cursor = "not-allowed";
      }
    }, false);

    this.$refs.layersbar.addEventListener("drop", ( event )=> {
      event.preventDefault();
      if ( event.target.className.includes(outClassName) ) {
        this.$store.commit('mod_workspace/ADD_elToWorkspace', event)
      }
    }, false);
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
      return this.$store.getters['mod_workspace/currentNetwork']
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
      this.openLoadDialog(this.dialogLoadFile, opt)
    },
    eventSaveNetwork() {
      this.dialogSaveNetwork()
    }
  },
  methods: {
    openLoadDialog,
    dialogLoadFile(pathArr) {
      fs.readFile(pathArr[0],
        (err, data)=> {
        if(data) {
          let net = JSON.parse(data.toString());
          this.$store.commit('mod_workspace/ADD_loadNetwork', net)
        }
        else {
          console.error(err);
        }
      });
    },
    dialogSaveNetwork() {
      const dialog = remote.dialog;
      const network = this.currentNetwork;
      const jsonNet = cloneNet(network);

      dialog.showSaveDialog((fileName) => {
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
