import html2canvas  from 'html2canvas';
import canvg        from 'canvg'
import {remote}     from 'electron'
import fs           from 'fs';


import TextEditable     from '@/components/base/text-editable.vue'
import NetworkField     from '@/components/network-field/network-field.vue'
import GeneralSettings  from "@/components/global-popups/workspace-general-settings.vue";
import GeneralResult    from "@/components/global-popups/workspace-result";
import SelectCoreSide   from "@/components/global-popups/workspace-core-side";
import TheStatistics    from "@/components/statistics/the-statistics.vue";
import TheTesting       from "@/components/statistics/the-testing.vue";
import TheViewBox       from "@/components/statistics/the-view-box";
import { mapActions } from 'vuex';

export default {
  name: 'WorkspaceContent',
  components: {
    NetworkField, TextEditable,
    GeneralSettings, GeneralResult,
    SelectCoreSide,
    TheStatistics, TheTesting, TheViewBox,
  },
  data() {
    return {
      showTestingTab: false,
    }
  },
  computed: {
    scaleNet: {
      get: function () {
        let zoom = this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom * 100;
        return Math.round(zoom);
      },
      set: function (newValue) {
        this.$store.dispatch('mod_workspace/SET_statusNetworkZoom', newValue/100);
      }
    },
    workspace() {
      return this.$store.state.mod_workspace.workspaceContent
    },
    indexCurrentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
    hideSidebar() {
      return this.$store.state.globalView.hideSidebar
    },
    showGlobalSet() {
      return this.$store.state.globalView.globalPopup.showNetSettings
    },
    showGlobalResult() {
      return this.$store.state.globalView.globalPopup.showNetResult
    },
    hasStatistics() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkStatistics;
    },
    showCoreSide() {
      return this.$store.state.globalView.globalPopup.showCoreSideSettings
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    statisticsIsOpen() {
      return this.$store.getters['mod_workspace/GET_statisticsIsOpen']
    },
    statisticsElSelected() {
      return this.$store.state.mod_statistics.selectedElArr
    },
    testIsOpen() {
      return this.$store.getters['mod_workspace/GET_testIsOpen']
    },
    statusNetworkCore() {
      return this.$store.getters['mod_workspace/GET_networkCoreStatus']
    },
    currentNet() {
      this.scale = this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
    },
    currentNetwork() {
      return this.$store.getters['mod_workspace/GET_currentNetwork']
    },
    currentSelectedEl() {
      return this.$store.getters['mod_workspace/GET_currentSelectedEl']
    },
    isTutorialMode() {
      return this.$store.getters['mod_tutorials/getIstutorialMode']
    },
    tutorialActiveStep() {
      return this.$store.getters['mod_tutorials/getActiveStep']
    },
    networkClass() {
      this.calcScaleMap();
      return {
        'open-statistic': this.statisticsIsOpen,
        'open-test': this.testIsOpen
      }
    }
  },
  watch: {
    statusNetworkCore(newStatus) {
      if(newStatus === 'Finished' && this.showTestingTab === false) {
        this.$store.dispatch('globalView/NET_trainingDone');
        this.$store.dispatch('mod_workspace/EVENT_startDoRequest', false);
        this.showTestingTab = true;
      }
    },
    '$store.state.mod_events.saveNetwork': {
      handler() {
        this.saveNetwork();
      }
    },
    currentSelectedEl(newStatus, oldStatus) {
      if(newStatus.length > 0 && this.isTutorialMode && this.tutorialActiveStep === 'training') {
        this.$store.dispatch('mod_tutorials/pointActivate', {way: 'next', validation: newStatus[0].el.layerMeta.tutorialId});
      } 
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    calcScaleMap() {
      this.$nextTick(()=> {
        const net = this.$refs.networkField[0].$refs.network;
        const scaleH = net.offsetHeight/net.scrollHeight;
        const scaleW = net.offsetWidth/net.scrollWidth;
        const maxScale = scaleH < scaleW ? scaleH : scaleW;
        this.scaleNet = +maxScale.toFixed(1) * 100
      })
    },
    scaleScroll(e) {
      e.wheelDelta > 0 ? this.incScale() : this.decScale();
    },
    deleteTabNetwork(index) {
      this.$store.commit('mod_workspace/DELETE_network', index)
    },
    setTabNetwork(index) {
      this.$store.commit('mod_workspace/SET_currentNetwork', index);
      this.$store.dispatch('mod_workspace/SET_elementUnselect');
      if(this.statisticsIsOpen !== null) this.$store.dispatch('mod_workspace/SET_openStatistics', false);
      if(this.testIsOpen !== null) this.$store.dispatch('mod_workspace/SET_openTest', false);
    },
    toggleSidebar() {
      this.$store.commit('globalView/SET_hideSidebar', !this.hideSidebar)
    },
    decScale() {
      if (this.scaleNet <= 30) {
        this.scaleNet = 30
      }
      else this.scaleNet = this.scaleNet - 5
    },
    incScale () {
      if (this.scaleNet > 95) {
        this.scaleNet = 100
      }
      else this.scaleNet = this.scaleNet + 5
    },
    // resize(newRect, i) {
    //   //console.log(newRect);
    //   //console.log(i);
    //   // this.network[i].meta.top = newRect.top;
    //   // this.network[i].meta.left = newRect.left;
    // },
    // onActivated(e) {
    //   //console.log(e)
    // },
    editNetName(newName) {
      this.$store.dispatch('mod_workspace/SET_networkName', newName);
    },
    openStatistics(i) {
      this.setTabNetwork(i);
      this.$store.dispatch('mod_statistics/STAT_defaultSelect', null);
      this.$store.dispatch('mod_workspace/SET_openStatistics', true);
      this.$store.dispatch('mod_events/EVENT_chartResize');
    },
    openTest(i) {
      this.setTabNetwork(i);
      this.$store.dispatch('mod_statistics/STAT_defaultSelect', null);
      this.$store.dispatch('mod_workspace/SET_openTest', true);
      this.$store.dispatch('mod_events/EVENT_chartResize');
    },
    saveNetwork() {
      const dialog = remote.dialog;
      const network = this.currentNetwork;
      doScreenShot(this)
        .then((img)=> {
          const stringNet = cloneNet(network, img);
          openSaveDialog(stringNet)
        })
        .catch((err)=> {console.log(err)})


      function openSaveDialog(jsonNet) {
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

            alert("The file has been successfully saved");
            savePathToLocal(JSON.parse(jsonNet).project, fileName)
          });
        });
      }

      function doScreenShot(ctx) {
        return new Promise((resolve, reject)=> {
          const workspace = ctx.$refs.workspaceNet;
          const svg = workspace.querySelector('.svg-arrow');
          const arrowsCanvas = document.createElement('canvas');
          arrowsCanvas.style.position = "absolute";
          arrowsCanvas.style.zIndex = '0';
          ctx.$refs.infoSectionName[0].appendChild(arrowsCanvas);
          canvg(arrowsCanvas, svg.outerHTML);
          svg.style.display = 'none';
          const options = {
            scale: 1, //180x135
          };
          return html2canvas(workspace, options)
            .then((canvas)=> {
              resolve(canvas.toDataURL());
              svg.style.display = 'block';
              arrowsCanvas.remove();
            });
        })
      }
      function savePathToLocal(project, path) {
        let localProjectsList = localStorage.getItem('projectsList');
        let projectsList = [];
        if(localProjectsList) {
          projectsList = JSON.parse(localProjectsList);
          let indexIdProj = projectsList.findIndex((proj)=> proj.id === project.id);
          if(indexIdProj >= 0) {
            project.path = [];
            project.path.push(path);
            projectsList[indexIdProj] = project;
          }
        }
        project.path = [];
        project.path.push(path);
        projectsList.push(project);
        localStorage.setItem('projectsList', JSON.stringify(projectsList))
      }
      function cloneNet(net, imgPath) {
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
            image: imgPath,
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
    trainingFinished(index) {
      let networkStatus = this.workspace[index].networkMeta.coreStatus.Status;
      return networkStatus === 'Finished' || networkStatus === 'Testing';
    },
    trainingInProcess(index) {
      let networkStatus = this.workspace[index].networkMeta.coreStatus.Status;
      return networkStatus === 'Training' || networkStatus === 'Validation';
    },
    trainingWaiting(index) {
      return this.workspace[index].networkMeta.coreStatus.Status === 'Waiting';
    }
  }
}