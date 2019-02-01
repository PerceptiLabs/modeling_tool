import fs from 'fs';
import {remote} from 'electron'

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
    this.addDragListener();
    if(process.env.BUILD_TARGET !== 'web') {
      this.$store.dispatch('mod_api/API_runServer');
    }
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
          savePathToLocal(JSON.parse(jsonNet).project, fileName)
        });
      });
      function savePathToLocal(project, path) {
        let localProjectsList = localStorage.getItem('projectsList');
        let projectsList = [];
        if(localProjectsList) {
          projectsList = JSON.parse(localProjectsList);
          let findIdProj = projectsList.findIndex((proj)=> proj.id === project.id);
          if(findIdProj >= 0) {
            return
          }
        }
        project.path = [];
        project.path.push(path)
        projectsList.push(project);
        localStorage.setItem('projectsList', JSON.stringify(projectsList))
      }
      function cloneNet(net) {
        //clone network
        var outNet = {};
        for (var key in net) {
          if(key === 'networkElementList') {
            outNet[key] = JSON.parse(cloneEl(net[key]))
          }
          else {
            outNet[key] = net[key];
          }
        }
        outNet.networkMeta = {};
        //create project
        let time = new Date();
        var timeOptions = {
          year: 'numeric',
          month: 'numeric',
          day: 'numeric',
          timezone: 'UTC',
          hour: 'numeric',
          minute: 'numeric',
        };
        let toJson = {
          project: {
            time: time.toLocaleString("ru", timeOptions),
            image: "data:image/png;base64,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",
            name: outNet.networkName,
            id: outNet.networkID,
            trainedPath: '',
            isCloud: false
          },
          network: outNet
        };
        return JSON.stringify(toJson, null, ' ');
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
